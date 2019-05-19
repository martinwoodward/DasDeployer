try:
    from local_settings import *
except ImportError:
    pass

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import pprint

# Create a connection to the org
credentials = BasicAuthentication('', PAT)
connection = Connection(base_url=ORG_URL, creds=credentials)

# Get the build status
build_client = connection.clients.get_build_client()
buildDef = build_client.get_definition(PROJECT, BUILD_PIPELINE_ID, include_latest_builds=True)

if buildDef.latest_completed_build.id == buildDef.latest_build.id:
    print("Build " + buildDef.latest_build.definition.name + " " + buildDef.latest_build.build_number + " " + buildDef.latest_completed_build.result)
else:
    # A build is in progress
    print("Build " + buildDef.latest_build.definition.name + " " + buildDef.latest_build.build_number + " " + buildDef.latest_completed_build.result + " (" + buildDef.latest_build.status + ")")

# Look for release approvals
rm_client = connection.clients.get_release_client()

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




