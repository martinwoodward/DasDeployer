try:
    from local_settings import *
except ImportError:
    pass

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import pprint

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

