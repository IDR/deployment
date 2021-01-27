# IDR Monitoring

Each IDR deployment has its own monitoring system.

## Metrics

Day to day performance of the IDR can be visualised using Grafana, which is accessible using an anonymous account on idr-management:

    ssh idr-proxy -L 3000:management:3000

Open http://localhost:3000/.
The dashboards of interest are accessed from the `Home` menu:
- IDR PostgreSQL: The numbers of database rows and locks in use
- IDR sessions: Numbers of OMERO sessions and web requests. Note that quantiles are calculated over a fixed window, and will be very inaccurate if the number of requests is low.
- IDR vertical: CPU, active memory, load and network usage for all servers.

### Prometheus

If you want to query the raw metrics directly you can connect to prometheus:

    ssh idr-proxy -L 9090:management:9090

Open http://localhost:9090/ and you can interactively query the metrics using [PromQL (Prometheus Query Language)](https://prometheus.io/docs/prometheus/latest/querying/basics/).


## Centralised logging

The IDR has a experimental centralised logging collector using Fluentd, ElasticSearch and Kibana:

    ssh idr-proxy -L 5601:management:5601

Open http://localhost:5601/.
Limitations:
- An index pattern `logstash-*` may need to be create on the first access
- The ElasticSearch server is not clustered and has limited querying capacity. It can be easily overloaded.
- Logs are kept for two weeks.


## IDR Pilot Monitoring

All IDR pilot test instances are currently monitored by a single monitoring server.
This is accessed using the same commands as above, using `idr-pilot` as the proxy.


## IDR FTP Monitoring

The IDR FTP server has limited Prometheus monitoring running on the same server with alerts for low available disk space.


## Long term log analysis

More structure analysis of archived IDR access logs across multiple releases is handled in https://github.com/IDR/idr-log-analysis


## Deployment

All monitoring (central server and node agents) are deployed by the `ansible/management*.yml` playbooks.

### Prometheus

The central Prometheus server runs in a Docker container deployed by an [Ansible rolse](https://github.com/ome/ansible-role-prometheus) and [a playbook](../ansible/management-prometheus.yml).
The templated prometheus configuration can be fetched from `/etc/prometheus/prometheus.yml` if necessary for investigation, and the templated alerting rules are written to `/etc/prometheus/rules/`.

This playbook also deploys all the required [Prometheus exporters](https://prometheus.io/docs/instrumenting/exporters/) on all nodes.


### Grafana

Grafana runs in Docker and is [deployed by a playbook](../ansible/management-grafana.yml).
The playbook automatically configures Grafana and uploads some pre-created dashboards using Grafana's REST API.


### ElasticSearch, Kibana, Fluentd

ElasticSearch, Kibana and the Fluentd server are run in Docker and [deployed by a playbook](../ansible/management-fluentd.yml).
This playbook also deploys the Fluentd logging agents that collect the logs on the OMERO and proxy servers, and forward them to the central Fluentd server.
