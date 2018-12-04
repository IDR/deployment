# IDR default molecule test for Travis

This tests a minimal IDR: PostgreSQL, OMERO read-write, Nginx proxy.

It is designed to run within the limited resources provided by Travis CI so is not a complete test of the IDR.
For instance, the OMERO read-only servers are not installed due to limited memory.
