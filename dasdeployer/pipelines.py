try:
    from local_settings import *
except ImportError:
    pass

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

import threading, queue

class QueryResultStatus():
    CHECKING = "Checking"
    BUILD_COMPLETE = "Build Complete"
    BUILD_IN_PROGRESS = "Building"

class QueryResult():
    def __init__(self, result_status=QueryResultStatus.CHECKING):
        self.status = result_status
        self.last_build = None
        self.latest_build = None
        self.enable_dev = False
        self.enable_stage = False
        self.enable_prod = False
        self.deploying_dev = False
        self.deploying_stage = False
        self.deploying_prod = False
        self.dev_release = None
        self.stage_release = None
        self.prod_release = None

class Pipelines():
    def __init__(self):
        self._poll_thread = None

    def get_status(self):
        if self._poll_thread is None:
            self._poll_thread = PollStatusThread(interval=10)
            self._poll_thread.start()
        return self._poll_thread._last_result
    
    def approve(self, approve_env):
        print("Approve env:" + approve_env)
        # Get Release Client
        connection = Connection(base_url=ORG_URL, creds=BasicAuthentication('', PAT))
        rm_client = connection.clients.get_release_client()
        approvals = rm_client.get_approvals(project=PROJECT, type_filter="preDeploy")
        releaseApproval = None
        for a in approvals:
            # print(a.release.name + " awaiting approval to " + a.release_environment.name)
            if approve_env == a.release_environment.name:
                # Approve this environment
                approval = a
                approval.status = "approved"
                approval.comments = "Approved by DasDeployer big button"
                releaseApproval = rm_client.update_release_approval(approval, PROJECT, approval.id)
                print("Approved " + releaseApproval.release.name + " to " + releaseApproval.release_environment.name)
        return releaseApproval




class PollStatusThread(threading.Thread):
    def __init__(self, interval=10):
        super(PollStatusThread, self).__init__()
        self.daemon = True
        self.stoprequest = threading.Event()
        
        self.regularInterval = interval
        self.delay = interval

        self._connection = Connection(base_url=ORG_URL, creds=BasicAuthentication('', PAT))
        self._build_client = self._connection.clients.get_build_client()
        self._rm_client = self._connection.clients.get_release_client()

        self._last_result = QueryResult()

    def start(self):
        self.stoprequest.clear()
        super(PollStatusThread, self).start()

    def stop(self, timeout=10):
        self.stoprequest.set()
        self.join(timeout)

    def join(self, timeout=None):
        super(PollStatusThread, self).join(timeout)
        if self.is_alive():
            assert timeout is not None
            raise RuntimeError(
                "PollStatusThread failed to die within %d seconds" % timeout)

    def run(self):
        while True:
            # Wait a bit then poll the server again
            result = QueryResult()

            buildDef = self._build_client.get_definition(PROJECT, BUILD_PIPELINE_ID, include_latest_builds=True)

            if buildDef.latest_completed_build.id == buildDef.latest_build.id:
                result.status = QueryResultStatus.BUILD_COMPLETE
                result.latest_build = buildDef.latest_build
                result.last_build = buildDef.latest_completed_build
            else:
                # A build is in progress
                result.status = QueryResultStatus.BUILD_IN_PROGRESS
                result.latest_build = buildDef.latest_build
                result.last_build = buildDef.latest_completed_build

            # Figure out if we should enable approval toggles

            # First see if any of the environments are deploying
            for e in ENVIRONMENTS:
                deployments = self._rm_client.get_deployments(PROJECT, definition_id=RELEASE_ID, definition_environment_id=ENVIRONMENTS[e], top=1, deployment_status="all")
                deploy_env = (deployments[0].deployment_status == "inProgress" or deployments[0].operation_status == "QueuedForAgent")
                enable_env = (deployments[0].deployment_status == "inProgress" or deployments[0].deployment_status == "notDeployed")
                
                if e == 'Dev':
                    result.enable_dev = enable_env
                    result.deploying_dev = deploy_env
                    result.dev_release = deployments[0].release
                elif e == 'Stage':
                    result.enable_stage = enable_env
                    result.deploying_stage = deploy_env
                    result.stage_release = deployments[0].release
                elif e == 'Prod':
                    result.enable_prod = enable_env
                    result.deploying_prod = deploy_env
                    result.prod_release = deployments[0].release  
                
                #if deploy_env:
                #    print(deployments[0])
                #    print(e + ": " + deployments[0].release.name + " - " + deployments[0].deployment_status + " q:" + deployments[0].queued_on.strftime("%Y-%m-%d %H:%M") )

            if (self._last_result.status != result.status or 
                 (self._last_result.latest_build is not None and 
                  self._last_result.latest_build.last_changed_date != result.latest_build.last_changed_date
                 ) or
                 self._last_result.enable_dev != result.enable_dev or
                 self._last_result.enable_stage != result.enable_stage or
                 self._last_result.enable_prod != result.enable_prod or
                 self._last_result.deploying_dev != result.deploying_dev or
                 self._last_result.deploying_stage != result.deploying_stage or
                 self._last_result.deploying_prod != result.deploying_prod
                ):
                # Something has changed
                print("change")
                self._last_result = result

            # At the end of the thread execution, wait a bit and then poll again
            if self.stoprequest.wait(self.delay):
                break


def pipemain():

    # Create a connection to the org
    connection = Connection(base_url=ORG_URL, creds=BasicAuthentication('', PAT))

    # Get the build status
    build_client = connection.clients.get_build_client()
    buildDef = build_client.get_definition(PROJECT, BUILD_PIPELINE_ID, include_latest_builds=True)

    if buildDef.latest_completed_build.id == buildDef.latest_build.id:
        print("Build " + buildDef.latest_build.definition.name + " " + buildDef.latest_build.build_number + " " + buildDef.latest_completed_build.result)
    else:
        # A build is in progress
        print("Build " + buildDef.latest_build.definition.name + " " + buildDef.latest_build.build_number + " " + buildDef.latest_completed_build.result + " (" + buildDef.latest_build.status + ")")

    # Get Release Client
    rm_client = connection.clients.get_release_client()

    # See what environments we have and the status of their latest deployments
    release = rm_client.get_release_definition(PROJECT, RELEASE_ID)
    for e in release.environments:
        deployments = rm_client.get_deployments(PROJECT, definition_id=RELEASE_ID, definition_environment_id=e.id, top=1, deployment_status="all")
        print(str(e.id) + " - " + e.name + ": " + deployments[0].release.name + " - " + deployments[0].deployment_status )

    # Look up pending approvals
    approvals = rm_client.get_approvals(project=PROJECT, type_filter="preDeploy")

    for a in approvals:
        print(a.release.name + " awaiting approval to " + a.release_environment.name)

    if len(approvals) > 0:
        # Approve one of them
        approval = approvals[0]
        approval.status = "approved"
        approval.comments = "Approved by DasDeployer"
        releaseApproval = rm_client.update_release_approval(approval, PROJECT, approval.id)
        print("Approved " + releaseApproval.release.name + " to " + releaseApproval.release_environment.name)

