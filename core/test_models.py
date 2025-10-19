from django.test import TestCase
from core.models import Asset


class AssetModelTest(TestCase):
    def test_create_asset(self):
        a = Asset.objects.create(code='A001', name='Máy chiếu', location='Phòng 101')
        self.assertEqual(str(a), 'A001 - Máy chiếu')
