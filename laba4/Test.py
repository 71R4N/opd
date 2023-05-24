import unittest
from app import app


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_index_get(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_post_with_file(self):
        with open('test.txt', 'w') as f:
            f.write('hello world world')

        with open('test.txt', 'rb') as f:
            response = self.app.post('/', data={'file': (f, 'test.txt')})

        result_html = response.data.decode()

        # check if most_frequent_word is in the rendered HTML
        self.assertIn('<h1>Самое частое слово: world</h1>', result_html)

    def test_post_empty_file(self):
        with open('test.txt', 'w') as f:
            f.write('')

        with open('test.txt', 'rb') as f:
            response = self.app.post('/', data={'file': (f, 'test.txt')})

        result_html = response.data.decode()

        # check if most_frequent_word is in the rendered HTML
        self.assertIn('<h1>Файл пуст</h1>', result_html)


if __name__ == '__main__':
    unittest.main()