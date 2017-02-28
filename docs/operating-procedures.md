# IDR administration

If you used the OpenStack provisioning playbook, the only accessible external ports will be `22`, `80` and `443` on `idr-proxy`.
For all administrative OMERO operations you will first need to SSH into `idr-proxy` and/or set up a SSH tunnel for other ports and servers.

Any changes that do not involve manipulating the data stored in OMERO (such as changes to the OMERO.server and OMERO.web configuration) should be done by modifying the deployment playbooks to ensure they are included in future deployments.


## Production IDR

There are two ways to access the production IDR:
- Nginx web proxy running on `idr-proxy`
- Back-end OMERO.web and OMERO.server running on `idr-omero`


### `idr-proxy`
The IDR appears as a read-only resource to public users, so the Nginx proxy has a custom caching configuration that ignores any headers sent by the back-end OMERO.web.
This should only be used for public web access, otherwise private tokens or views may inadvertently be cached.

This means if the back-end OMERO data is modified the cache may become stale.
A special cache-buster port `9000` is configured on `idr-proxy`.
Any requests to this port will force a cache refresh.
In the case of large screens this may lead to a significant slowdown of the server, though it does also show the importance of the cache.

You can force a complete refresh of the cache by removing everything under `/var/cache/nginx/`.


### `idr-omero`
If you SSH into this server you will have full access to OMERO.server, including OMERO.web and the command-line client.
If you need to login to OMERO you should always connect to this server.

If you need to restart OMERO.server or OMERO.web, you must use `systemctl` and not `omero admin` or `omero web`.


## Analysis IDR

External users of the VAE should connect to JupyterHub via the front-end `idr-proxy`.
For internal administration you may need to work on:
- `idr-a-omero`: A clone of the production OMERO to ensure complex analysis queries do not affect public users of the IDR
- `idr-a-dockermanager`: The Docker server running the individual VAEs


### `idr-a-dockermanager`
JupyterHub runs in a Docker container managed as a systemd service, and spawns additional Docker containers for analysis users.


## Backups, restores and upgrades

The IDR has a well-defined separation between applications and data.
The following directories contain data that must be backed up:
- `idr-omero:/data`: The OMERO data directory
- `idr-database:/var/lib/pgsql`: The PostgreSQL data directory

The following directories are not essential but you may wish to also back them up:
- `idr-proxy:/var/cache/nginx`: The front-end web cache (can be regenerated)
- `idr-a-omero:/data`: The analysis OMERO data directory (clone of production)
- `idr-a-database:/var/lib/pgsql`: The PostgreSQL data directory (clone of production)
- `idr-a-dockermanager:/data`: Jupyter notebooks (VAEs are treated as ephemeral)

If you used the OpenStack provisioning playbook, these are all separate volumes that can be backed up using the OpenStack clients.

### Restoration
If you need to restore the IDR, it is sufficient to restore these directories into a clean CentOS 7 server before running the deployment playbooks, which will take the existing data into account when installing the IDR.
The OpenStack provisioning playbook includes optional parameters to specify existing volumes to be copied.

### New releases
The public-facing IDR is read-only and we aim to minimize any downtime, so instead of upgrading the existing system the procedure for new releases involves cloning the existing server volumes into a new system:

- Ensure you have an unused floating IP.
- Run the OpenStack provisioning playbook with an alternative IDR environment parameter (`idr_environment_idr=newidr`) and set the existing volumes as the source for the new volumes.
- When you are ready to go live disassociate the floating IPs from the production and new deployments, and associate the previous production floating IP with the new deployment.
