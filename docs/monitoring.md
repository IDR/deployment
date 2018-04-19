# IDR Monitoring

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

Open http://localhost:9090/.


## Centralised logging

The IDR has a experimental centralised logging collector using Fluentd, ElasticSearch and Kibana:

    ssh idr-proxy -L 5601:management:5601

Open http://localhost:5601/.
Limitations:
- An index pattern `logstash-*` may need to be create on the first access
- The ElasticSearch server is not clustered and has limited querying capacity. It can be easily overloaded.
- Logs are kept for two weeks.
