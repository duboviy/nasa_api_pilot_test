import unittest
# Python 2 and 3 compatible code
try:
    from itertools import izip as zip  # py 2.x series
except ImportError:  # py 3.x series
    pass

import nasa_wrapper as api
from images import is_equal_images, get_img


class NasaApiPilotTest(unittest.TestCase):
    """ The purpose of the test is to check images which are made by specified rover (e.g. Curiosity). """
    @classmethod
    def setUpClass(cls):
        cls.sol = 1000
        cls.amount = 10  # limit of first photos to check
        cls.rover = 'curiosity'  # NASA API provides photos for several rovers (not only Curiosity)
        cls.threshold = 10  # if any camera made N times more images than any other (e.g. 10) - test fails

        cls.by_sol_all = api.get_rover_photos(cls.rover, sol=cls.sol)  # all photos by sol
        cls.by_sol = cls.by_sol_all[:cls.amount]  # custom photos amount by sol

        cls.earth_date = api.earth_date_equals_to_sol_from_api(cls.by_sol)
        # all photos by earth date below
        cls.by_earth_date_all = api.get_rover_photos(cls.rover, earth_date=cls.earth_date)
        cls.by_earth_date = cls.by_earth_date_all[:cls.amount]  # custom photos amount by earth date

    def test_get_photos_by_sol(self):
        self.assertEqual(len(self.by_sol), self.amount,
                         msg="expected custom amount %d of photos" % self.amount)

    def test_get_photos_by_earth_date(self):
        self.assertEqual(len(self.by_earth_date), self.amount,
                         msg="expected custom amount %d of photos" % self.amount)

    def test_earth_date_value_provided_by_api_with_obtained_using_formula(self):
        landing_date = api.rover_landing_date_from_api(self.by_sol)
        sol_to_earth_date = api.sol_to_earth_date_by_formula(self.sol, landing_date)

        self.assertEqual(self.earth_date, sol_to_earth_date,
                         msg="value provided by API: {}, but expected earth date by formula {}"
                         .format(self.earth_date, sol_to_earth_date))

    def test_sol_earth_photos_equality(self):
        """ Compare photos by sol and by earth date. Check metadata and perform image comparison. """
        # NASA API provides sorted list with photos, compare lists right away - photo urls match
        self.assertListEqual(self.by_sol, self.by_earth_date,
                             msg="expected that photos should be equal")

        for photo_sol, photo_earth_date in zip(self.by_sol, self.by_earth_date):
            self.assertDictEqual(photo_sol, photo_earth_date,
                                 msg="expected that photos metadata should be equal")
            # metadata checked, image comparison below
            img1, img2 = get_img(photo_sol['img_src']), get_img(photo_earth_date['img_src'])
            self.assertTrue(is_equal_images(img1, img2))

    def test_bonus_camera_photos_distribution(self):
        """
        Determine how many pictures were made by each camera (by Curiosity on 1000 sol.).
        This test uses manifests API to get cameras list and request photos with specified camera.
        If any camera made N times more images than any other (e.g. 10) - test fails.
        real e.g. {'CHEMCAM': 4, 'FHAZ': 2, 'MAHLI': 0, 'MARDI': 0, 'NAVCAM': 3, 'RHAZ': 2}
        less 10 times than 'MAST': 838
        """
        cameras_dist = api.photo_cameras_distribution(self.rover, self.sol)
        low_dist_cameras = api.low_dist_cameras(cameras_dist, self.threshold)

        self.assertFalse(low_dist_cameras,
                         msg="These cameras made 10 times less photos than %s - max photos amount by camera"
                             % max(cameras_dist.values()))

    def test_bonus_camera_photos_distribution_naive_brute_force_way(self):
        """
        Determine how many pictures were made by each camera (by Curiosity on 1000 sol.).
        This test NOT uses manifests API to get cameras list and request photos with specified camera.
        It's NOT efficient way as used in test_bonus_camera_photos_distribution,
        but can be used for additional check of proper work of NASA API.
        If any camera made N times more images than any other (e.g. 10) - test fails.
        real e.g. {'CHEMCAM': 4, 'FHAZ': 2, 'MAHLI': 0, 'MARDI': 0, 'NAVCAM': 10, 'RHAZ': 2}
        less 10 times than 'MAST': 838
        """
        cameras_dist = api.get_rover_cameras_naive_brute_force_way(self.by_sol_all, self.rover)
        low_dist_cameras = api.low_dist_cameras(cameras_dist, self.threshold)

        self.assertFalse(low_dist_cameras,
                         msg="These cameras made 10 times less photos than %s - max photos amount by camera"
                             % max(cameras_dist.values()))

    def test_additional_compare_low_dist_camera_photos_from_api_and_naive_brute_force_way(self):
        """
        This test uses both ways to fetch camera photos distribution and compare them:
        1) Request photos with specified camera within NASA API (api.get_rover_photos(..., camera=cam))
        2) Naive inefficient brute force way to get dist to make additional check of proper work of NASA API

        Test catches NASA API "buggy" behaviour with NAVCAM camera name, else cameras fetched properly:
        - {'CHEMCAM': 4, 'FHAZ': 2, 'MAHLI': 0, 'MARDI': 0, 'NAVCAM': 3, 'RHAZ': 2}
        ?                                                             ^
        + {'CHEMCAM': 4, 'FHAZ': 2, 'MAHLI': 0, 'MARDI': 0, 'NAVCAM': 10, 'RHAZ': 2}
        ?                                                             ^^
        """
        cameras_dist = api.photo_cameras_distribution(self.rover, self.sol)
        low_dist_with_spec_cam = api.low_dist_cameras(cameras_dist, self.threshold)

        cameras_dist = api.get_rover_cameras_naive_brute_force_way(self.by_sol_all, self.rover)
        low_dist_without_spec_cam = api.low_dist_cameras(cameras_dist, self.threshold)

        assertion_msg = """
        low camera photos distributions fetched with and without specifying camera in API request are not equal.
        API "Buggy" behaviour - both ways should return the photos amount for each camera.
        """
        self.assertDictEqual(low_dist_with_spec_cam, low_dist_without_spec_cam,
                             msg=assertion_msg)


if __name__ == '__main__':
    unittest.main()
