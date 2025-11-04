# Red Hat OpenShift developer sandbox demo

## Creating a developer sandbox 

1. Go to https://sandbox.redhat.com/ 

2. Create Developer Account or Log In in case you have it.
    * Provide additional information
    * Agree and Submit

3. Select OpenShift and Try it

## Importing the source code from Git

4. In your sandbox Namespace / Project
   * Select Workloads -> Topology 
   * Right click somewhere in the project area -> Import from ...

5. Select git repo: https://github.com/rflorenc/litemaas-chatbot.git
    * Show advanced git
        * Context dir should be: /rlteam

6. Deploy Resource Type should be Deployment

7. Click Create

## Final steps

### Download oc command line tool 

In the sandbox cluster:
  * click '?' (Top Right) next to your username.
  * select Command Line Tools
  * Download oc for your target architecture (arm64 / x86_64)

In the terminal, ensure that:
  * you are logged in via oc command line
    * copy log in command: select Copy login command, from your account drop-down (Top Right)
    * Display token and copy to your terminal
  * you are in your sandbox namespace
    * oc project $your_sandbox_namespace

```
export YOUR_OPENSHIFT_NAMESPACE=your_sandbox_namespace

oc set env deployment/litemaas-chatbot-git -n $YOUR_OPENSHIFT_NAMESPACE LITEMAAS_BASE_URL=

oc set env deployment/litemaas-chatbot-git -n $YOUR_OPENSHIFT_NAMESPACE LITEMAAS_API_KEY=
```

Once the build finishes and the pod is ready.
Open the route and try the chat app by writting "Hello Open Source!". 
