Searchengine installation and configuration using Ansible:
==========================================================

There is an ansible playbook (management-searchengine.yml) that has been written to deploy the apps:
* It will config and run searchengine, Elasticsearch and searchengine client
* It will configure and create the required folders
* It will configure the three apps and run them
* There is a variables file (groups_vars/management-searchengine-hosts.yml) that the user needs to edit before running the playbook
    * The variable names are self-explained
* To check that the apps have been installed and run, the user can use wget or curl to call:
  * for searchengine, http://127.0.0.1:5556/api/v2/resources/
  * for searchengine client, http://127.0.0.1:5556
  * for Elasticsearch, http://127.0.0.1:9201  
* After deploying the apps using the playbook, it is needed to run another playbook for caching and indexing:
    * run_searchengine_index_cache_services.yml    
    * If the Postgresql database server is located at the same machine which hosts the searchengine, it is needed to:
        * Edit pg_hba.conf file (one of the postgresql configuration files) and add two client ips (i.e. 10.11.0.10 and 10.11.0.11)
        * Reload the configuration; so the PostgreSQL accepts the connection from indexing and caching services.
    * As the caching and indexing processes take a long time, there are another two playbooks that enable the user to check if they have finished or not:
        * check_indexing_service.yml
        * check_caching_service.yml