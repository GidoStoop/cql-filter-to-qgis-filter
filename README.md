# cql-filter-to-qgis-filter

QGIS server plugin

Intercepts the CQL_FILTER query string parameter normally used for geoserver filtering in a WMS request and transforms it to a FILTER query string parameter so it works on qgis server WMS. Usefull when you want to load a WMS in a viewer with filtering options, but have no control over the constructed query by the viewer.
