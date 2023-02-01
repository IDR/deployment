OMERO search engine installation and configuration
==================================================

The [idr-elasticsearch.yml](../ansible/idr-elasticsearch.yml) and [idr-searchengine.yml](../ansible/idr-searchengine.yml) playbooks deploy the OMERO
search engine stack:

*   It will config and run the Elasticsearch cluster and [OMERO searchengine](https://github.com/ome/omero_search_engine).     
*   It will configure and create the required folders
*   It will configure the two apps and run them
*   Additional configuration can be controlled via the
    [group variables file](../ansible/groups_vars/searchengine-hosts.yml)

To check that the apps have been installed and run, the user can use `wget` or `curl` to call:

  * for the OMERO search engine, http://127.0.0.1:5577/searchengine/api/v1/resources/
  * for Elasticsearch, http://127.0.0.1:9201
  * for Elasticsearch cluster, http://127.0.0.1:9201/_cluster/health?pretty

After deploying the apps using the playbook, the
[run_searchengine_index_service.yml](../ansible/run_searchengine_index_service.yml)
playbook needs to be executed to run the caching and indexing.

As the indexing process takes a long time, the [check_indexing_service.yml](../ansible/check_indexing_service.yml)
playbooks allows the user to check if it have finished or not.
