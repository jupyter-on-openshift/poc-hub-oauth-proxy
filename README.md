JupyterHub (OAuth Proxy)
========================

This repository contains a sample application for deploying JupyterHub as a means to provide Jupyter notebooks to multiple users. Authentication of users is managed using an OAuth enabled proxy and Keycloak.

**Note: This sample application is a demonstration only, do not use this in practice. This is because ``oauth2-proxy`` and Keycloak don't play nicely together and the cookies generated when trying to pass an access token through to JupyterHub, in order to properly protect access, are too large and are rejected by browsers. This means that JupyterHub can't be protected properly from users running the Jupyter notebooks through JupyterHub.**

Deploying the application
-------------------------

To deploy the sample application, you can run:

```
oc new-app https://raw.githubusercontent.com/jupyter-on-openshift/poc-hub-oauth-proxy/master/templates/jupyterhub.json
```

This will create all the required builds and deployments from the one template.

If desired, you can instead load the template, with instantiation of the template done as a separate step from the command line or using the OpenShift web console.

Resource requirements
---------------------

If deploying to an OpenShift environment that enforces quotas, you must have a memory quota for terminating workloads (pods) of 3GiB so that builds can be run. For one user, you will need 6GiB of quota for terminating workloads (pods). Each additional user requires 1GiB.

For storage, two 1GiB persistent volumes are required for the PostgreSQL databases for Keycloak and JupyterHub. Further, each user will need a 1GiB volume for notebook storage.

Registering a user
------------------

Keycloak will be deployed, with JupyterHub and Keycloak automatically configured to handle authentication of users. No users are setup in advance, but users can register themselves by clicking on the _Register_ link on the login page.

For this to work though, because ``oauth2-proxy`` expects email addressed to be verified, you would need to configure Keycloak with SMTP server details and enable email verification for users in Keycloak. If this is not done, you will need to manually mark emails address of any users as verified through Keycloak admin interface before they can access JupyterHub.
