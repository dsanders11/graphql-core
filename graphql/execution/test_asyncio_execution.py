# flake8: noqa
import pytest
import asyncio
import functools
from graphql.error import format_error
from graphql.execution import execute
from graphql.language.parser import parse
from graphql.type import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLField,
    GraphQLString
)


async def test_asyncio_py35_executor():
    ast = parse('query Example { a, b, c }')

    async def resolver(context, *_):
        await asyncio.sleep(0.001)
        return 'hey'

    async def resolver_2(context, *_):
        await asyncio.sleep(0.003)
        return 'hey2'

    def resolver_3(context, *_):
        return 'hey3'

    Type = GraphQLObjectType('Type', {
        'a': GraphQLField(GraphQLString, resolver=resolver),
        'b': GraphQLField(GraphQLString, resolver=resolver_2),
        'c': GraphQLField(GraphQLString, resolver=resolver_3)
    })

    result = await execute(GraphQLSchema(Type), ast)
    assert not result.errors
    assert result.data == {'a': 'hey', 'b': 'hey2', 'c': 'hey3'}


async def test_asyncio_py35_executor_return_promise():
    ast = parse('query Example { a, b, c }')

    async def resolver(context, *_):
        await asyncio.sleep(0.001)
        return 'hey'

    async def resolver_2(context, *_):
        await asyncio.sleep(0.003)
        return 'hey2'

    def resolver_3(context, *_):
        return 'hey3'

    Type = GraphQLObjectType('Type', {
        'a': GraphQLField(GraphQLString, resolver=resolver),
        'b': GraphQLField(GraphQLString, resolver=resolver_2),
        'c': GraphQLField(GraphQLString, resolver=resolver_3)
    })

    result = await execute(GraphQLSchema(Type), ast, return_promise=True)
    assert not result.errors
    assert result.data == {'a': 'hey', 'b': 'hey2', 'c': 'hey3'}


async def test_asyncio_py35_executor_with_error():
    ast = parse('query Example { a, b }')

    async def resolver(context, *_):
        await asyncio.sleep(0.001)
        return 'hey'

    async def resolver_2(context, *_):
        await asyncio.sleep(0.003)
        raise Exception('resolver_2 failed!')

    Type = GraphQLObjectType('Type', {
        'a': GraphQLField(GraphQLString, resolver=resolver),
        'b': GraphQLField(GraphQLString, resolver=resolver_2)
    })

    result = await execute(GraphQLSchema(Type), ast)
    formatted_errors = list(map(format_error, result.errors))
    assert formatted_errors == [{'locations': [{'line': 1, 'column': 20}], 'message': 'resolver_2 failed!'}]
    assert result.data == {'a': 'hey', 'b': None}