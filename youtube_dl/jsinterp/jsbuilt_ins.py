from __future__ import unicode_literals

from types import FunctionType


class JSBase(object):

    def __init__(self, name, value):
        self.props = self.__class__.props.copy()
        self.name = name
        self.value = value

    def __str__(self):
        return '[native code]'

    props = {}


def js(func):
    def py2js(o):
        if isinstance(o, (FunctionType, JSBase)):
            return JSFunctionPrototype(o)
        elif isinstance(o, dict):
            return JSObjectPrototype(o)
        elif isinstance(o, (list, tuple)):
            return JSArrayPrototype(o)
        else:
            raise NotImplementedError

    def wrapper(*args, **kwargs):
        return py2js(func(*args, **kwargs))

    return wrapper


class JSProtoBase(JSBase):

    def __init__(self):
        cls = self.__class__
        while cls is not JSProtoBase:
            cls = cls.__base__
            props = cls.props.copy()
            props.update(self.props)
            self.props = props
        super(JSProtoBase, self).__init__('', self.props)

    def __str__(self):
        return ''

    def _get_prop(self, prop):
        result = self.value.get(prop)
        if result is None:
            result = self.props.get(prop)
        return result

    @js
    def get_prop(self, prop):
        return self._get_prop(prop)

    @js
    def call_prop(self, prop, *args):
        return self._get_prop(prop)(self, *args)


class JSObjectPrototype(JSProtoBase):

    def __init__(self, value=None):
        super(JSObjectPrototype, self).__init__()
        if value is not None:
            self.value = value

    def _to_string(self):
        return 'object to string'

    def _to_locale_string(self):
        return 'object to locale string'

    def _value_of(self):
        return 'object value of'

    def _has_own_property(self, v):
        return v in self.value

    def _is_prototype_of(self, v):
        return 'object has own prop'

    def _is_property_enumerable(self, v):
        return 'object is property enumerable'

    props = {
        'constructor': __init__,
        'toString': _to_string,
        'toLocaleString': _to_locale_string,
        'valueOf': _value_of,
        'hasOwnProperty': _has_own_property,
        'isPrototypeOf': _is_prototype_of,
        'propertyIsEnumerable': _is_property_enumerable
    }


class JSObject(JSBase):

    def __init__(self):
        super(JSObject, self).__init__(self.name, self.props)

    def _get_prototype_of(self, o):
        return 'object get prototype of'

    def _get_own_property_descriptor(self, o, p):
        return 'object desc'

    def _get_own_property_names(self, o):
        return list(o.value.keys())

    def _create(self, o, props=None):
        return 'object create'

    def _define_property(self, o, p, attr):
        return 'object define prop'

    def _define_properties(self, o, props):
        return 'object define properties'

    def _seal(self, o):
        return 'object seal'

    def _freeze(self, o):
        return 'object freeze'

    def _prevent_extensions(self, o):
        return 'object prevent extension'

    def _is_sealed(self, o):
        return 'object is sealed'

    def _is_frozen(self, o):
        return 'object is frozen'

    def _is_extensible(self, o):
        return 'object is extensible'

    def _keys(self, o):
        return 'object keys'

    name = 'Object'
    props = {
        'length': 1,
        'prototype': JSObjectPrototype.props,
        'getPrototypeOf': _get_prototype_of,
        'getOwnPropertyDescriptor': _get_own_property_descriptor,
        'getOwnPropertyNames': _get_own_property_names,
        'create': _create,
        'defineProperty': _define_property,
        'defineProperties': _define_properties,
        'seal': _seal,
        'freeze': _freeze,
        'preventExtensions': _prevent_extensions,
        'isSealed': _is_sealed,
        'isFrozen': _is_frozen,
        'isExtensible': _is_extensible,
        'keys': _keys
    }


class JSFunctionPrototype(JSObjectPrototype):

    def __init__(self, *args):
        body = args[-1] if args else ''
        if isinstance(body, JSBase):
            super(JSFunctionPrototype, self).__init__(body.props)
            self.fname = body.name
        else:
            super(JSFunctionPrototype, self).__init__()
            self.fname = 'anonymous'

        # FIXME: JSProtoBase sets body to '' instead of None
        self.body = str(body)
        self.args = [sarg.strip() for arg in args[:-1] for sarg in str(arg).split(',')]
        # TODO check if self._args can be parsed as formal parameter list
        # TODO check if self._body can be parsed as function body
        # TODO set strict
        # TODO throw strict mode exceptions
        # (double argument, "eval" or "arguments" in arguments, function identifier is "eval" or "arguments")

    @property
    def _length(self):
        # FIXME: returns maximum instead of "typical" number of arguments
        # Yeesh, I dare you to find anything like that in the python specification.
        return len(self.args)

    def _to_string(self):
        if self.body is not None:
            body = '\n'
            body += '\t' + self.body if self.body else self.body
        else:
            body = ''
        return 'function %s(%s) {%s\n}' % (self.fname, ', '.join(self.args), body)

    def _apply(self, this_arg, arg_array):
        return 'function apply'

    def _call(self, this_arg, *args):
        return 'function call'

    def _bind(self, this_arg, *args):
        return 'function bind'

    props = {
        'length': 0,
        'constructor': __init__,
        'toString': _to_string,
        'apply': _apply,
        'call': _call,
        'bind': _bind
    }


class JSFuction(JSObject):

    name = 'Function'

    props = {
        'length': 1,
        'prototype': JSFunctionPrototype()
    }


class JSArrayPrototype(JSObjectPrototype):

    def __init__(self, value=None, length=0):
        super(JSArrayPrototype, self).__init__()
        self.list = [] if value is None else value
        self.value['length'] = self._length

    @property
    def _length(self):
        return len(self.list)

    def __str__(self):
        return 'JSArrayPrototype: %s' % self.list

    def __repr__(self):
        return 'JSArrayPrototype(%s, %s)' % (self.list, self._length)

    def _to_string(self):
        return 'array to string'

    def _to_locale_string(self):
        return 'array to locale string'

    def _concat(self, *items):
        return 'array concat'

    def _join(self, sep):
        return 'array join'

    def _pop(self):
        return 'array pop'

    def _push(self, *items):
        return 'array push'

    def _reverse(self):
        return 'array reverse'

    def _shift(self):
        return 'array shift'

    def _slice(self, start, end):
        return 'array slice'

    def _sort(self, cmp):
        return 'array sort'

    def _splice(self, start, delete_count, *items):
        return 'array splice'

    def _unshift(self, *items):
        return 'array unshift'

    def _index_of(self, elem, from_index=0):
        return 'array index of'

    def _last_index_of(self, elem, from_index=None):
        if from_index is None:
            from_index = len(self.value) - 1
        return 'array index of'

    def _every(self, callback, this_arg=None):
        return 'array every'

    def _some(self, callback, this_arg=None):
        return 'array some'

    def _for_each(self, callback, this_arg=None):
        return 'array for_each'

    def _map(self, callback, this_arg=None):
        return 'array map'

    def _filter(self, callback, this_arg=None):
        return 'array filter'

    def _reduce(self, callback, init=None):
        return 'array reduce'

    def _reduce_right(self, callback, init=None):
        return 'array reduce right'

    props = {
        'length': 0,
        'constructor': __init__,
        'toString': _to_string,
        'toLocaleString': _to_locale_string,
        'concat': _concat,
        'join': _join,
        'pop': _pop,
        'push': _push,
        'reverse': _reverse,
        'shift': _shift,
        'slice': _slice,
        'sort': _sort,
        'splice': _splice,
        'unshift': _unshift,
        'indexOf': _index_of,
        'lastIndexOf': _last_index_of,
        'every': _every,
        'some': _some,
        'forEach': _for_each,
        'map': _map,
        'filter': _filter,
        'reduce': _reduce,
        'reduceRight': _reduce_right
    }


class JSArray(JSObject):

    name = 'Array'

    def _is_array(self, arg):
        return 'array is array'

    props = {
        'length': 1,
        'prototype': JSArrayPrototype.props,
        'isArray': _is_array
    }

global_obj = JSObjectPrototype({'Object': JSObject(),
                                'Array': JSArray(),
                                'Function': JSFuction()})
