import warnings
from decimal import Decimal
from django.test import TestCase
from restless.models import serialize, flatten
from .testapp.models import Publisher, Author, Book


class TestSerialization(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name='User Foo')
        self.publisher = Publisher.objects.create(name='Publisher')
        self.books = []
        for i in range(10):
            b = self.author.books.create(
                author=self.author,
                title='Book %d' % i,
                isbn='123-1-12-123456-%d' % i,
                price=Decimal("10.0"),
                publisher=self.publisher
            )
            self.books.append(b)

    def test_full_shallow(self):
        """Test simple serialization, all fields, without recursing"""

        s = serialize(self.author)
        self.assertEqual(s, {'name': 'User Foo', 'id': self.author.id})

    def test_partial_shallow(self):
        """Test serialization of only selected fields"""

        s = serialize(self.author, ['name'])
        self.assertEqual(s, {'name': 'User Foo'})

    def test_shallow_foreign_key_serialization(self):
        """Test that foreign key fields are serialized as integer IDs."""

        s = serialize(self.books[0])
        self.assertEqual(s['author'], self.author.id)

    def test_serialize_related_deprecated(self):
        """Test serialization of related model"""

        with warnings.catch_warnings(record=True):
            s = serialize(self.author, related={'books': None})
        self.assertEqual(s['name'], 'User Foo')
        self.assertEqual(len(s['books']), len(self.books))
        for b in s['books']:
            self.assertTrue(b['title'].startswith('Book '))
            self.assertTrue(b['isbn'].startswith('123-1-12-123456-'))

    def test_serialize_related(self):
        """Test serialization of related model"""

        s = serialize(self.author, include=[('books', dict())])
        self.assertEqual(s['name'], 'User Foo')
        self.assertEqual(len(s['books']), len(self.books))
        for b in s['books']:
            self.assertTrue(b['title'].startswith('Book '))
            self.assertTrue(b['isbn'].startswith('123-1-12-123456-'))

    def test_serialize_related_partial_deprecated(self):
        """Test serialization of some fields of related model"""

        with warnings.catch_warnings(record=True):
            s = serialize(self.author, related={
                'books': ('title', None, False)
            })
        self.assertEqual(s['name'], 'User Foo')
        self.assertEqual(len(s['books']), len(self.books))
        for b in s['books']:
            self.assertTrue(b['title'].startswith('Book '))
            self.assertTrue('isbn' not in b)

    def test_serialize_related_partial(self):
        """Test serialization of some fields of related model"""

        s = serialize(self.author, include=[
            ('books', dict(
                fields=['title']
            ))
        ])
        self.assertEqual(s['name'], 'User Foo')
        self.assertEqual(len(s['books']), len(self.books))
        for b in s['books']:
            self.assertTrue(b['title'].startswith('Book '))
            self.assertTrue('isbn' not in b)

    def test_serialize_related_deep_deprecated(self):
        """Test serialization of twice-removed related model"""

        with warnings.catch_warnings(record=True):
            s = serialize(self.author, related={
                'books': (None, {
                    'publisher': None,
                }, None)
            })

        self.assertEqual(s['name'], 'User Foo')
        self.assertEqual(len(s['books']), len(self.books))
        for b in s['books']:
            self.assertTrue(b['title'].startswith('Book '))
            self.assertEqual(b['publisher']['name'], 'Publisher')

    def test_serialize_related_deep(self):
        """Test serialization of twice-removed related model"""

        s = serialize(self.author, include=[
            ('books', dict(
                include=[('publisher', {})]
            ))
        ])

        self.assertEqual(s['name'], 'User Foo')
        self.assertEqual(len(s['books']), len(self.books))
        for b in s['books']:
            self.assertTrue(b['title'].startswith('Book '))
            self.assertEqual(b['publisher']['name'], 'Publisher')

    def test_serialize_related_flatten_deprecated(self):
        """Test injection of related models' fields into the serialized one"""

        b = self.books[0]
        s = serialize(b, related={
            'author': (None, None, True)
        })
        self.assertEqual(s['name'], b.author.name)

    def test_serialize_related_flatten(self):
        """Test injection of related models' fields into the serialized one"""

        b = self.books[0]
        s = serialize(b, fields=[
            ('author', dict())
        ], fixup=flatten('author'))

        self.assertEqual(s['name'], b.author.name)

    def test_serialize_queryset(self):
        """Test queryset serialization"""

        Author.objects.all().delete()
        a1 = Author.objects.create(name="foo")
        a2 = Author.objects.create(name="bar")
        qs = Author.objects.all()
        _ = list(qs)  # force sql query execution

        # Check that the same (cached) queryset is used, instead of a clone
        with self.assertNumQueries(0):
            s = serialize(qs)

        self.assertEqual(s,
            [
                {'name': a1.name, 'id': a1.id},
                {'name': a2.name, 'id': a2.id},
            ]
        )

    def test_serialize_list(self):
        """Test that list serialization deep-serializes list elements"""

        Author.objects.all().delete()
        a1 = Author.objects.create(name="foo")
        a2 = Author.objects.create(name="bar")
        s = serialize(list(Author.objects.all()))
        self.assertEqual(s,
            [
                {'name': a1.name, 'id': a1.id},
                {'name': a2.name, 'id': a2.id},
            ]
        )

    def test_serialize_dict(self):
        """Test that dict serialization deep-serializes dict values"""

        Author.objects.all().delete()
        a1 = Author.objects.create(name="foo")
        a2 = Author.objects.create(name="bar")
        s = serialize({'a1': a1, 'a2': a2})

        self.assertEqual(s['a1']['name'], a1.name)
        self.assertEqual(s['a2']['name'], a2.name)

    def test_serialize_set(self):
        """
        Test that set serialization deep-serializes set values and
        returns a list (since sets can't contain a dict and aren't JSON
        serializable).
        """

        Author.objects.all().delete()
        a1 = Author.objects.create(name="bar")
        a2 = Author.objects.create(name="foo")
        s = serialize(set(Author.objects.all()))
        self.assertTrue(isinstance(s, list))
        # Must cast back to set to ignore ordering
        self.assertEqual(sorted(s, key=lambda el: el['name']), [
            {'name': a1.name, 'id': a1.id},
            {'name': a2.name, 'id': a2.id},
        ])

    def test_passthrough(self):
        """Test that non-ORM types just pass through the serializer"""

        data = {'a': ['b', 'c'], 'd': 1, 'e': "foo"}
        self.assertEqual(data, serialize(data))

    def test_serialize_takes_fields_tuple(self):
        s = serialize(self.author, fields=('id',), include=('name',))
        self.assertEqual(s, {
            'id': self.author.id,
            'name': self.author.name
        })

    def test_serialize_doesnt_mutate_fields(self):
        runs = [0]

        def accessor(obj):
            runs[0] += 1
            return 'foo'

        # If fields are appended on, 'desc' will be twice in the list
        # for the second run, so in total the accessor function will be
        # run 3 instead of 2 times
        serialize([self.author, self.author], fields=['id'],
            include=[('desc', accessor)])

        self.assertEqual(runs[0], 2)
