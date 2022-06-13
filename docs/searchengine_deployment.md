OMERO search engine installation and configuration
==================================================

The [idr-searchengine.yml](../ansible/idr-searchengine.yml) playbook deploys the OMERO
search engine stack:

*   It will config and run the [OMERO searchengine](https://github.com/ome/omero_search_engine),
    Elasticsearch and the [OMERO search engine client](https://github.com/ome/omero_search_engine_client/)
*   It will configure and create the required folders
*   It will configure the three apps and run them
*   Additional configuration can be controlled via the
    [group variables file](../ansible/groups_vars/searchengine-hosts.yml)

To check that the apps have been installed and run, the user can use `wget` or `curl` to call:

  * for the OMERO search engine, http://127.0.0.1:5577/searchengine/api/v1/resources/
  * for OMERO search engine client, http://127.0.0.1:5567
  * for Elasticsearch, http://127.0.0.1:9201  

After deploying the apps using the playbook, the
[run_searchengine_index_service.yml](../ansible/run_searchengine_index_service.yml)
playbook needs to be executed to run the caching and indexing.

As the indexing process takes a long time, the [check_indexing_service.yml](../ansible/check_indexing_service.yml)
playbooks allows the user to check if it have finished or not.
