import json
import sys
from   abc import ABCMeta, abstractmethod
from   tornado.httpclient import AsyncHTTPClient, HTTPRequest
import tornado.ioloop

PY2 = sys.version_info[0] == 2
if PY2:
    from urllib import urlencode
else:
    from urllib.parse import urlencode


class SolrConfigurationError(Exception):
    pass

class SolrClient(object):

    __metaclass__ = ABCMeta

    def __init__(self,
            host         = 'localhost',
            port         = 8983,
            prefix       = '',
            method       = 'http',
            ssl          = False,
            verify_certs = True,
            ca_certs     = '',
            ioloop       = None,
            *args,
            **kwargs
    ):
        self.base_url = "%s://%s:%s%s" % (method, host, port, prefix)
        self.certs    = ca_certs
        self.client   = AsyncHTTPClient(
            ioloop or tornado.ioloop.IOLoop.current()
        )

    def mk_req(self, url, **kwargs):
        """
        Helper function to create a tornado HTTPRequest object, kwargs get passed in to
        create the HTTPRequest object. See:
        `Request Object <http://tornado.readthedocs.org/en/latest/httpclient.html#request-objects>`_
        """
        req_url = self.base_url + url
        req_kwargs = kwargs
        req_kwargs['ca_certs'] = req_kwargs.get('ca_certs', self.certs)
        # have to do this because tornado's HTTP client doesn't play nice
        req_kwargs['allow_nonstandard_methods'] = req_kwargs.get(
            'allow_nonstandard_methods',
            True
        )
        return HTTPRequest(req_url, **req_kwargs)

    def mk_url(self, *args, **kwargs):
        """
        Args get parameterized into base url:
            *(foo, bar, baz) -> /foo/bar/baz
        Kwargs get encoded and appended to base url:
            **{'hello':'world'} -> /foo/bar/baz?hello=world
        """
        params = urlencode(kwargs)
        url = '/' + '/'.join([x for x in args if x])
        if params:
            url += '?' + params
        return url

    def _post_json(self, url, body, callback=None, req_kwargs={}):
        req_kwargs.update({'headers':{'Content-Type':'application/json'}})

        request = self.mk_req(
            url,
            method = 'POST',
            body   = json.dumps(body),
            **req_kwargs
        )

        self.client.fetch(request, callback=callback)

    def query(self,
            collection,
            q,
            callback    = None,
            indent      = 'off',
            req_kwargs  = {},
            wt          = 'json'
        ):

        """
        `Request api <https://cwiki.apache.org/confluence/display/solr/JSON+Request+API>`_

        :arg collection: The name of the collection
        :arg q:          Query dictionary
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        q.update({'indent':indent, 'wt':wt})
        url = self.mk_url('solr', collection, 'query', **q)

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def add_json_document(self,
        collection,
        doc,
        boost        = 1,
        callback     = None,
        indent       = 'off',
        overwrite    = True,
        commitWithin = 1000,
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        `json api <https://cwiki.apache.org/confluence/display/solr/Uploading+Data+with+Index+Handlers#UploadingDatawithIndexHandlers-JSONFormattedIndexUpdates>`_

        :arg collection:   The name of the collection
        :arg boost:        Boosted weight
        :arg CommitWithin: Commit within time (ms)
        :arg doc:          Dictionary to be uploaded
        :arg callback:     Callback to run on completion
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """

        url = self.mk_url(
            'solr', collection, 'update',
            **{'indent':indent, 'wt':wt}
        )

        j = json.dumps({
            'add': {
                'boost':        boost,
                'commitWithin': commitWithin,
                'doc':          doc,
                'overwrite':    overwrite,
            }
        })

        self._post_json(url, j, req_kwargs=req_kwargs, callback=callback)

    def add_json_documents(self,
        collection,
        docs,
        boost        = 1,
        callback     = None,
        commitWithin = 1000,
        indent       = 'off',
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        `json api <https://cwiki.apache.org/confluence/display/solr/Uploading+Data+with+Index+Handlers#UploadingDatawithIndexHandlers-JSONFormattedIndexUpdates>`_

        :arg collection:   The name of the collection
        :arg docs:         Dictionary to be uploaded
        :arg boost:        Boosted weight
        :arg CommitWithin: Commit within time (ms)
        :arg callback:     Callback to run on completion
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """
        url = self.mk_url('solr', collection, 'update',
            **{'indent':indent, 'wt':wt}
        )
        self._post_json(url, docs, req_kwargs=req_kwargs,
            callback=callback
        )

    def update_json(self,
        collection,
        upjson,
        callback    = None,
        indent      = 'off',
        req_kwargs  = {},
        wt          = 'json'
    ):
        """
        `json api <https://cwiki.apache.org/confluence/display/solr/Uploading+Data+with+Index+Handlers#UploadingDatawithIndexHandlers-JSONFormattedIndexUpdates>`_

        :arg collection: The name of the collection
        :arg upjson:     Json to be posted
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        url = self.mk_url('solr', collection, 'update', **{'indent':indent, 'wt':wt})
        self._post_json(url, upjson, req_kwargs=req_kwargs, callback=callback)

    def delete(self,
        collection,
        docs,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        :arg collection: The name of the collection
        :arg docs:       Document id(s) to delete
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """

        url = self.mk_url('solr', collection, 'update', **{'indent':indent, 'wt':wt})
        j   = json.dumps({'delete': [docs]})
        self._post_json(url, j, req_kwargs=req_kwargs, callback=callback)

    def core_status(self,
        callback   = None,
        core       = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `status <https://cwiki.apache.org/confluence/display/solr/CoreAdmin+API#CoreAdminAPI-STATUS>`_

        :arg callback:   Callback to run on completion
        :arg core:       The name of the core
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        kw = {}
        if core:
            kw['core'] = core

        kw.update({'wt':wt, 'indent':indent})

        url     = self.mk_url('solr', 'admin', 'cores', **kw)
        request = self.mk_req(url, **req_kwargs)

        self.client.fetch(request, callback=callback)

    def core_create(self,
        name,
        callback     = None,
        config       = '',
        indent       = 'off',
        instance_dir = None,
        req_kwargs   = {},
        schema       = '',
        wt           = 'json'
    ):
        """
        `create <https://cwiki.apache.org/confluence/display/solr/CoreAdmin+API#CoreAdminAPI-CREATE>`_

        :arg name:       The name of the core
        :arg callback:   Callback to run on completion
        :arg config:     Configuration file to use
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        kw = {
            'action':      'CREATE',
            'indent':      indent,
            'name':        name,
            'schema':      schema,
            'wt':          wt,
        }

        if config:
            kw.update({'config':config})

        if instance_dir :
            kw.update({'instanceDir':instance_dir})

        url     = self.mk_url('solr', 'admin', 'cores', **kw)
        request = self.mk_req(url, **req_kwargs)

        self.client.fetch(request, method='POST', callback=callback)

    def core_reload(self,
        core,
        callback     = None,
        indent       = 'off',
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        `reload <https://cwiki.apache.org/confluence/display/solr/CoreAdmin+API#CoreAdminAPI-RELOAD>`_

        :arg core:       Core to reload
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg name:       The name of the core
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """

        kw = {
            'action': 'RELOAD',
            'core':   core,
            'indent': indent,
            'wt':     wt,
        }

        url     = self.mk_url('solr', 'admin', 'cores', **kw)
        request = self.mk_req(url, **req_kwargs)

        self.client.fetch(request, method='POST', callback=callback)

    def core_rename(self,
        core,
        other,
        callback     = None,
        indent       = 'off',
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        `rename <https://cwiki.apache.org/confluence/display/solr/CoreAdmin+API#CoreAdminAPI-RENAME>`_

        :arg core:       Core to be renamed
        :arg other:      Other name for core
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg name:       The name of the core
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        kw = {
            'action': 'RENAME',
            'core':   core,
            'other':  other,
            'indent': indent,
            'wt':     wt,
        }

        url     = self.mk_url('solr', 'admin', 'cores', **kw)
        request = self.mk_req(url, **req_kwargs)

        self.client.fetch(request, method='POST', callback=callback)

    def core_swap(self,
        core,
        other,
        callback     = None,
        indent       = 'off',
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        `swap <https://cwiki.apache.org/confluence/display/solr/CoreAdmin+API#CoreAdminAPI-SWAP>`_

        :arg core:       Core to be renamed
        :arg other:      Other name for core
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg name:       The name of the core
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        kw = {
            'action': 'SWAP',
            'core':   core,
            'other':  other,
            'indent': indent,
            'wt':     wt,
        }

        url     = self.mk_url('solr', 'admin', 'cores', **kw)
        request = self.mk_req(url, **req_kwargs)

        self.client.fetch(request, callback=callback)

    def core_unload(self,
        core,
        callback     = None,
        del_index    = None,
        del_data_dir = None,
        del_inst_dir = None,
        indent       = 'off',
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        `unload <https://cwiki.apache.org/confluence/display/solr/CoreAdmin+API#CoreAdminAPI-UNLOAD>`_

        :arg core:         Core to remove
        :arg callback:     Callback to run on completion
        :arg del_index:    Remove index
        :arg del_data_dir: Remove data directory and subdirectories
        :arg del_inst_dir: Remove everything related to core
        :arg indent:       Indent the response body
        :arg name:         The name of the core
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """

        kw = {
            'action': 'UNLOAD',
            'core':   core,
            'indent': indent,
            'wt':     wt,
        }

        if del_index:
            kw.update({'deleteIndex':del_index})

        if del_data_dir:
            kw.update({'deleteDataDir':del_data_dir})

        if del_inst_dir:
            kw.update({'deleteInstanceDir':del_inst_dir})

        url     = self.mk_url('solr', 'admin', 'cores', **kw)
        request = self.mk_req(url, **req_kwargs)

        self.client.fetch(request, callback=callback)

    # XXX: CORE API -> MERGEINDEXES, SPLIT, REQUESTSTATUS

    def add_configset(self,
        name,
        base_configset,
        callback      = None,
        config_kwargs = {},
        indent        = 'off',
        req_kwargs    = {},
        wt            = 'json'
    ):
        """
        `Configsets <https://cwiki.apache.org/confluence/display/solr/ConfigSets+API>`_

        :arg name:           Name of configset
        :arg base_configset: Name of base configset
        :arg callback:       Callback to run on completion
        :arg config_kwargs:  Additional configuration
        :arg indent:         Indent the response body
        :arg req_kwargs:     Optional tornado HTTPRequest kwargs
        :arg wt:             Response format: 'json' or 'xml'
        """
        url = self.mk_url(
            'admin', 'configs',
            **{
                'action':        'CREATE',
                'name':          name,
                'baseConfigSet': base_configset,
                'indent':        indent,
                'wt':            wt
            }
        )

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def delete_configset(self,
        name,
        callback      = None,
        indent        = 'off',
        req_kwargs    = {},
        wt            = 'json'
    ):
        """
        `Configsets <https://cwiki.apache.org/confluence/display/solr/ConfigSets+API>`_

        :arg name:       Name of configset
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        url = self.mk_url(
            'admin', 'configs',
            **{
                'action':        'DELETE',
                'name':          name,
                'indent':        indent,
                'wt':            wt
            }
        )

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def list_configset(self,
        callback      = None,
        indent        = 'off',
        req_kwargs    = {},
        wt            = 'json'
    ):
        """
        `Configsets <https://cwiki.apache.org/confluence/display/solr/ConfigSets+API>`_

        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        url = self.mk_url(
            'admin', 'configs',
            **{
                'action':        'LIST',
                'indent':        indent,
                'wt':            wt
            }
        )

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def schema(self,
        collection,
        callback    = None,
        indent      = 'off',
        req_kwargs  = {},
        wt          = 'json'
    ):
        """
        `Schema <https://cwiki.apache.org/confluence/display/solr/Schema+API>`_

        :arg collection: The name of the collection
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """

        url = self.mk_url('solr', collection, 'schema',
            **{'indent':indent, 'wt':wt}
        )

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def schema_fields(self,
        collection,
        callback   = None,
        field      = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `Schema Fields <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-ListFields>`_

        :arg collection: The name of the collection
        :arg callback:   Callback to run on completion
        :arg field:      Limit results to specific field
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        url = self.mk_url(
            'solr', collection, 'schema', 'fields', field,
            **{'indent':indent, 'wt':wt}
        )

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def schema_dynamic_fields(self,
        collection,
        callback   = None,
        field      = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json',
    ):
        """
        `Schema Dyanmic Fields <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-ListDynamicFields>`_

        :arg collection: The name of the collection
        :arg callback:   Callback to run on completion
        :arg field:      Limit results to specific field
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        url = self.mk_url(
            'solr', collection, 'schema', 'dynamicfields', field,
            **{'indent':indent, 'wt':wt}
        )

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def schema_field_types(self,
        collection,
        callback   = None,
        field      = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `Schema Field Types <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-ListFieldTypes>`_

        :arg collection: The name of the collection
        :arg callback:   Callback to run on completion
        :arg field:      Limit results to specific field
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        url = self.mk_url(
            'solr', collection, 'schema', 'fieldtypes', field,
            **{'indent':indent, 'wt':wt}
        )

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def schema_copy_fields(self,
        collection,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `Schema Copy Fields <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-ListCopyFields>`_

        :arg collection: The name of the collection
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        url = self.mk_url(
            'solr', collection, 'schema', 'copyfields',
            **{'indent':indent, 'wt':wt}
        )

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def schema_name(self,
        collection,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `Schema Name <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-ShowSchemaName>`_

        :arg collection: The name of the collection
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        url = self.mk_url(
            'solr', collection, 'schema', 'name',
            **{'indent':indent, 'wt':wt}
        )

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def schema_version(self,
        collection,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `Schema Version <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-ShowtheSchemaVersion>`_

        :arg collection: The name of the collection
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        url = self.mk_url(
            'solr', collection, 'schema', 'version',
            **{'indent':indent, 'wt':wt}
        )

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def schema_unique_key(self,
        collection,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `Schema Unique Keys <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-ListUniqueKey>`_

        :arg collection: The name of the collection
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        url = self.mk_url(
            'solr', collection, 'schema', 'uniquekey',
            **{'indent':indent, 'wt':wt}
        )

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def schema_similarity(self,
        collection,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `Schema Similarity <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-ShowGlobalSimilarity>`_

        :arg collection: The name of the collection
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        url = self.mk_url(
            'solr', collection, 'schema', 'similarity',
            **{'indent':indent, 'wt':wt}
        )

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def schema_default_operator(self,
        collection,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `Schema Default Operator <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-GettheDefaultQueryOperator>`_.

        :arg collection: The name of the collection
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        url = self.mk_url(
            'solr', collection, 'schema', 'solrqueryparser', 'defaultoperator',
            **{'indent':indent, 'wt':wt}
        )

        request = self.mk_req(url, **req_kwargs)
        self.client.fetch(request, callback=callback)

    def add_field(self,
        collection,
        name,
        field_type,
        callback     = None,
        field_kwargs = {},
        indent       = 'off',
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        For more information on `field types <https://cwiki.apache.org/confluence/display/solr/Defining+Fields>`_.
        Documentation for
        `adding new fields <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-AddaNewField>`_.

        :arg collection:   Collection name
        :arg name:         The name of the field
        :arg field_type:   Field type
        :arg callback:     Callback to run on completion
        :arg field_kwargs: Optional field type kwargs
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """

        url = self.mk_url(
            'solr', collection, 'schema',
            **{'indent':indent, 'wt':wt}
        )

        body = {"add-field": {
                "name": name,
                "type": field_type,
            }
        }
        body['add-field'].update(field_kwargs)

        self._post_json(url, body, req_kwargs=req_kwargs, callback=callback)

    def delete_field(self,
        collection,
        name,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        Documentation for `deleting fields <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-DeleteaField>`_

        :arg collection:   Collection name
        :arg name:         The name of the field
        :arg callback:     Callback to run on completion
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """

        url  = self.mk_url(
            'solr', collection, 'schema',
            **{'indent':indent, 'wt':wt}
        )
        body = {"delete-field": { "name": name }}

        self._post_json(url, body, req_kwargs=req_kwargs, callback=callback)

    def replace_field(self,
        collection,
        name,
        callback     = None,
        indent       = 'off',
        field_kwargs = {},
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        Documentation for `replacing fields <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-ReplaceaField>`_

        :arg collection:   Collection name
        :arg name:         The name of the field
        :arg callback:     Callback to run on completion
        :arg field_kwargs: Optional field type kwargs
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """

        url  = self.mk_url(
            'solr', collection, 'schema',
            **{'indent':indent, 'wt':wt}
        )

        body = {"replace-field": {"name": name} }
        body['replace-field'].update(field_kwargs)

        self._post_json(url, body, req_kwargs=req_kwargs, callback=callback)

    def add_dynamic_field(self,
        collection,
        name,
        field_type,
        callback     = None,
        field_kwargs = {},
        indent       = 'off',
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        For more information on `field types <https://cwiki.apache.org/confluence/display/solr/Defining+Fields>`_.
        Documentation for `adding new dynamic fields <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-AddaDynamicFieldRule>`_

        :arg collection:   Collection name
        :arg name:         The name of the field
        :arg field_type:   Field type
        :arg callback:     Callback to run on completion
        :arg field_kwargs: Optional field type kwargs
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """

        url = self.mk_url(
            'solr', collection, 'schema',
            **{'indent':indent, 'wt':wt}
        )

        body = {"add-dynamic-field": {
                "name": name,
                "type": field_type,
            }
        }
        body['add-dynamic-field'].update(field_kwargs)

        self._post_json(url, body, req_kwargs=req_kwargs, callback=callback)

    def delete_dynamic_field(self,
        collection,
        name,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        Documentation for `deleting dynamic fields <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-DeleteaDynamicFieldRule>`_

        :arg collection:   Collection name
        :arg name:         The name of the field
        :arg callback:     Callback to run on completion
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """

        url = self.mk_url(
            'solr', collection, 'schema',
            **{'indent':indent, 'wt':wt}
        )
        body = {"delete-dynamic-field": { "name": name }}

        self._post_json(url, body, req_kwargs=req_kwargs, callback=callback)

    def replace_dynamic_field(self,
        collection,
        name,
        callback     = None,
        indent       = 'off',
        field_kwargs = {},
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        Documentation for `replacing dynamic fields <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-ReplaceaDynamicFieldRule>`_.

        :arg collection:   Collection name
        :arg name:         The name of the field
        :arg callback:     Callback to run on completion
        :arg field_kwargs: Optional field type kwargs
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """

        url  = self.mk_url(
            'solr', collection, 'schema',
            **{'indent':indent, 'wt':wt}
        )

        body = {"replace-dynamic-field": { "name": name} }
        body['replace-dynamic-field'].update(field_kwargs)

        self._post_json(url, body, req_kwargs=req_kwargs, callback=callback)

    def add_field_type(self,
        collection,
        name,
        callback     = None,
        indent       = 'off',
        field_kwargs = {},
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        Documentation for `adding new field type <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-AddaNewFieldType>`_.

        :arg collection:   Collection name
        :arg name:         The name of the field
        :arg callback:     Callback to run on completion
        :arg field_kwargs: Optional field type kwargs
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """

        url  = self.mk_url(
            'solr', collection, 'schema',
            **{'indent':indent, 'wt':wt}
        )

        body = {"add-field-type": {
                "name": name,
                "type": field_type,
            }
        }
        body['add-field-type'].update(field_kwargs)

        self._post_json(url, body, req_kwargs=req_kwargs, callback=callback)

    def delete_field_type(self,
        collection,
        name,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        Documentation for `deleting field types <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-DeleteaFieldType>`_

        :arg collection:   Collection name
        :arg name:         The name of the field
        :arg callback:     Callback to run on completion
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """

        url = self.mk_url(
            'solr', collection, 'schema',
            **{'indent':indent, 'wt':wt}
        )
        body = {"delete-field-type": { "name": name }}

        self._post_json(url, body, req_kwargs=req_kwargs, callback=callback)

    def replace_field_type(self,
        collection,
        name,
        callback     = None,
        indent       = 'off',
        field_kwargs = {},
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        Documentation for `replacing field types <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-ReplaceaFieldType>`_

        :arg collection:   Collection name
        :arg name:         The name of the field
        :arg callback:     Callback to run on completion
        :arg field_kwargs: Optional field type kwargs
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """

        url  = self.mk_url(
            'solr', collection, 'schema',
            **{'indent':indent, 'wt':wt}
        )

        body = {"replace-field-type": {"name": name} }
        body['replace-field-type'].update(field_kwargs)

        self._post_json(url, body, req_kwargs=req_kwargs, callback=callback)

    def add_copy_field(self,
        collection,
        src,
        dst,
        callback   = None,
        indent     = 'off',
        maxChars   = None,
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        Documentation for `adding copy fields <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-AddaNewCopyFieldRule>`_

        :arg collection:   Collection name
        :arg src:          Source field name
        :arg dst:          Destination field name(s)
        :arg callback:     Callback to run on completion
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """

        url  = self.mk_url(
            'solr', collection, 'schema',
            **{'indent':indent, 'wt':wt}
        )

        body = {"add-copy-field": {
                "source": src,
                "dest": dst, #XXX: handle lists
            }
        }

        self._post_json(url, body, req_kwargs=req_kwargs, callback=callback)

    def delete_copy_field(self,
        collection,
        src,
        dst,
        callback   = None,
        indent     = 'off',
        maxChars   = None,
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        Documentation for `deleting a copy field <https://cwiki.apache.org/confluence/display/solr/Schema+API#SchemaAPI-DeleteaCopyFieldRule>`_

        :arg collection:   Collection name
        :arg src:          Source field name
        :arg dst:          Destination field name(s)
        :arg callback:     Callback to run on completion
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """

        url  = self.mk_url(
            'solr', collection, 'schema',
            **{'indent':indent, 'wt':wt}
        )

        body = {"delete-copy-field": {
                "source": src,
                "dest": dst, #XXX: handle lists
            }
        }

        self._post_json(url, body, req_kwargs=req_kwargs, callback=callback)

    def create_collection(self,
        collection,
        callback          = None,
        collection_kwargs = {},
        indent            = 'off',
        req_kwargs        = {},
        router_name       = 'compositeId',
        shards            = None,
        shards_per_node   = 1,
        replication       = 1,
        wt                = 'json'
    ):
        """
        `Create Collection <https://cwiki.apache.org/confluence/display/solr/Collections+API#CollectionsAPI-api1>`_

        :arg collection:        Collection name
        :arg collection_kwargs: Collection kwargs
        :arg callback:          Callback to run on completion
        :arg indent:            Indent the response body
        :arg req_kwargs:        Optional tornado HTTPRequest kwargs
        :arg router_name:       Either 'compositeId' or 'implicit'
        :arg wt:                Response format: 'json' or 'xml'
        """
        if shards:
            n_shards = len(shards.split(','))
        else:
            n_shards = 1

        if router_name not in ('compositeId', 'implicit'):
            raise SolrConfigurationError()

        collection_kwargs.update({
            'action':            'CREATE',
            'name':              collection,
            'indent':            indent,
            'numShards':         n_shards,
            'replicationFactor': replication,
            'maxShardsPerNode':  shards_per_node,
            'wt':                wt
        })

        url  = self.mk_url(
            'solr', 'admin', 'collections',
            **collection_kwargs
        )

        request = self.mk_req(url, method='POST', **req_kwargs)
        self.client.fetch(request, callback=callback)

    def reload_collection(self,
        collection,
        callback    = None,
        indent      = 'off',
        req_kwargs  = {},
        wt          = 'json'
    ):
        """
        `Reload Collection <https://cwiki.apache.org/confluence/display/solr/Collections+API#CollectionsAPI-api1>`_

        :arg collection: Collection name
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        collection_kwargs = {
            'action': 'RELOAD',
            'name':   collection,
            'indent': indent,
            'wt':     wt
        }

        url  = self.mk_url(
            'solr', 'admin', 'collections',
            **collection_kwargs
        )

        request = self.mk_req(url, method='POST', **req_kwargs)
        self.client.fetch(request, callback=callback)

    def split_shard_collection(self,
        collection,
        shard,
        callback     = None,
        shard_kwargs = {},
        indent       = 'off',
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        `Split Shard <https://cwiki.apache.org/confluence/display/solr/Collections+API#CollectionsAPI-api1>`_

        :arg collection:   Collection name
        :arg shard:        Shard id
        :arg shard_kwargs: Shard kwargs
        :arg callback:     Callback to run on completion
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """
        collection_kwargs = {
            'action':     'SPLITSHARD',
            'collection': collection,
            'shard':      shard,
            'indent':     indent,
            'wt':         wt
        }

        url  = self.mk_url(
            'solr', 'admin', 'collections',
            **collection_kwargs
        )

        request = self.mk_req(url, method='POST', **req_kwargs)
        self.client.fetch(request, callback=callback)

    def shard_collection(self,
        collection,
        shard,
        callback     = None,
        shard_kwargs = {},
        indent       = 'off',
        req_kwargs   = {},
        wt           = 'json'
    ):
        """
        `Shard Collection <https://cwiki.apache.org/confluence/display/solr/Collections+API#CollectionsAPI-api1>`_

        :arg collection:   Collection name
        :arg shard:        Shard id
        :arg shard_kwargs: Shard kwargs
        :arg callback:     Callback to run on completion
        :arg indent:       Indent the response body
        :arg req_kwargs:   Optional tornado HTTPRequest kwargs
        :arg wt:           Response format: 'json' or 'xml'
        """
        collection_kwargs = {
            'action':     'CREATESHARD',
            'collection': collection,
            'shard':      shard,
            'indent':     indent,
            'wt':         wt
        }

        url  = self.mk_url(
            'solr', 'admin', 'collections',
            **collection_kwargs
        )

        request = self.mk_req(url, method='POST', **req_kwargs)
        self.client.fetch(request, callback=callback)

    def delete_shard_collection(self,
        collection,
        shard,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `Delete Shard Collection <https://cwiki.apache.org/confluence/display/solr/Collections+API#CollectionsAPI-api1>`_

        :arg collection: Collection name
        :arg shard:      Shard id
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        collection_kwargs = {
            'action':     'DELETESHARD',
            'collection': collection,
            'shard':      shard,
            'indent':     indent,
            'wt':         wt
        }

        url  = self.mk_url(
            'solr', 'admin', 'collections',
            **collection_kwargs
        )

        request = self.mk_req(url, method='POST', **req_kwargs)
        self.client.fetch(request, callback=callback)

    def alias_collection(self,
        collections,
        name,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `Alias Collection <https://cwiki.apache.org/confluence/display/solr/Collections+API#CollectionsAPI-api1>`_

        :arg name:       Name of alias
        :arg collection: Collection(s) to alias
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        collection_kwargs = {
            'action':      'CREATEALIAS',
            'collections': collections,
            'indent':      indent,
            'name':        name,
            'wt':          wt
        }

        url  = self.mk_url(
            'solr', 'admin', 'collections',
            **collection_kwargs
        )

        request = self.mk_req(url, method='POST', **req_kwargs)
        self.client.fetch(request, callback=callback)

    def delete_alias_collection(self,
        name,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `Delete Alias Collection <https://cwiki.apache.org/confluence/display/solr/Collections+API#CollectionsAPI-api1>`_

        :arg name:       Name of alias
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        collection_kwargs = {
            'action': 'DELETEALIAS',
            'indent': indent,
            'name':   name,
            'wt':     wt
        }

        url  = self.mk_url(
            'solr', 'admin', 'collections',
            **collection_kwargs
        )

        request = self.mk_req(url, method='POST', **req_kwargs)
        self.client.fetch(request, callback=callback)

    def delete_collection(self,
        name,
        shard      = None,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `Delete Collection <https://cwiki.apache.org/confluence/display/solr/Collections+API#CollectionsAPI-api1>`_

        :arg name:       Name of alias
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        collection_kwargs = {
            'action': 'DELETE',
            'indent': indent,
            'name':   name,
            'shard':  shard or name,
            'wt':     wt
        }

        url  = self.mk_url(
            'solr', 'admin', 'collections',
            **collection_kwargs
        )

        request = self.mk_req(url, method='POST', **req_kwargs)
        self.client.fetch(request, callback=callback)

    def delete_replica_collection(self,
        collection,
        shard,
        replica,
        callback   = None,
        indent     = 'off',
        req_kwargs = {},
        wt         = 'json'
    ):
        """
        `Delete Replica Collection <https://cwiki.apache.org/confluence/display/solr/Collections+API#CollectionsAPI-api1>`_

        :arg collection: Name of collection
        :arg shard:      Shard id
        :arg replica:    Replica to be removed
        :arg callback:   Callback to run on completion
        :arg indent:     Indent the response body
        :arg req_kwargs: Optional tornado HTTPRequest kwargs
        :arg wt:         Response format: 'json' or 'xml'
        """
        collection_kwargs = {
            'action':     'DELETEREPLICA',
            'collection': collection,
            'indent':     indent,
            'replica':    replica,
            'shard':      shard,
            'wt':         wt
        }

        url  = self.mk_url(
            'solr', 'admin', 'collections',
            **collection_kwargs
        )

        request = self.mk_req(url, method='POST', **req_kwargs)
        self.client.fetch(request, callback=callback)
