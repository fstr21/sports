Source
Source Repo
fstr21/sports



Disconnect
Root Directory
Configure where we should look for your code. Docs↗
Root directory
mcp_leagues/soccer
Branch connected to production
Changes made to this GitHub branch will be automatically pushed to this environment.
Branch

main

Disconnect
Wait for CI
Trigger deployments after all GitHub actions have completed successfully.

Networking
Public Networking
Access your application over HTTP with the following domains
soccermcp-production.up.railway.app
Port 8080

 · 
Metal Edge




Domain
soccermcp-production
.up.railway.app

8080
Domain Available!


Cancel

Update

Custom Domain

TCP Proxy
Private Networking
Communicate with this service from within the Railway network.
soccer_mcp.railway.internal
IPv6


Ready to talk privately ·
You can also simply call me
soccer_mcp
.

DNS
soccer_mcp
.railway.internal

Endpoint name available!


Cancel

Update
Build
Builder
The value is set in
mcp_leagues/soccer/railway.toml
Open file↗

Dockerfile

Automatically Detected

Build with a Dockerfile using BuildKit. Docs↗

Custom Build Command
Override the default build command that is run when building your app. Docs↗
Build command
pip install -r requirements.txt
Watch Paths
Gitignore-style rules to trigger a new deployment based on what file paths have changed. Docs↗

Watch Paths
Deploy
Custom Start Command
Command that will be run to start new deployments. Docs↗
The value is set in
mcp_leagues/soccer/railway.toml
Open file↗
Start command
python soccer_mcp_server.py
Add pre-deploy step (Docs↗)
Regions
Configure how many instances of this service are deployed in each region.
US East (Virginia, USA)

Replicas
1
Instance
Multi-region replicas are only available on the Pro plan.

Learn More↗
Teardown
Configure old deployment termination when a new one is started. Docs↗

Resource Limits
Max amount of vCPU and Memory to allocate to each replica for this service.
CPU: 8 vCPU

Plan limit: 8 vCPU

Memory: 8 GB

Plan limit: 8 GB

Increase your resources
Cron Schedule
Run the service according to the specified cron schedule.

Cron Schedule
Healthcheck Path
Endpoint to be called before a deploy completes to ensure the new deployment is live. Docs↗
Healthcheck Path
/
Healthcheck Timeout
Number of seconds we will wait for the healthcheck to complete. Docs↗
Healthcheck Timeout
300
Serverless
Containers will scale down to zero and then scale up based on traffic. Requests while the container is sleeping will be queued and served when the container wakes up. Docs↗

Restart Policy
Configure what to do when the process exits. Docs↗
The value is set in
mcp_leagues/soccer/railway.toml
Open file↗
On Failure

Restart the container if it exits with a non-zero exit code.


Number of times to try and restart the service if it stopped due to an error.
The value is set in
mcp_leagues/soccer/railway.toml
Open file↗
Max restart retries
10
Config-as-code
Railway Config File
Manage your build and deployment settings through a config file. Docs↗

Add File Path
Delete Service
Deleting this service will permanently delete all its deployments and remove it from this environment. This cannot be undone.