import os
from django.conf import settings
from django.test import TestCase
import shutil
from filebrowser.functions import get_version_path, version_generator

__author__ = 'andriy'


class FunctionsTest(TestCase):
    def __init__(self, methodName='runTest'):
        super(TestCase, self).__init__(methodName)

    def setUp(self):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, "2"), True)
        os.mkdir(os.path.join(settings.MEDIA_ROOT, "2"))
        shutil.copy(os.path.join(settings.MEDIA_ROOT, "rss.gif"),
                    os.path.join(settings.MEDIA_ROOT, "2"))

    def test_get_version_path(self):
        for version in settings.FILEBROWSER_VERSIONS:
            version_generator("2/rss.gif", version)

        for version in settings.FILEBROWSER_VERSIONS:
            path = get_version_path("2/rss.gif", version)
            ends = "rss_" + version + ".gif"
            print("Path [%s] have to ends with [%s], version [%s]\n" % (path, ends, version))
            self.assertTrue(path.endswith(ends),
                            "Path [%s] is not ends with [%s]" % (path, ends,))

            for version2 in settings.FILEBROWSER_VERSIONS:
                path2 = get_version_path(path, version2)
                ends = "rss_" + version2 + ".gif"

                print("Path [%s] have to ends with [%s], version [%s->%s]\n" % (path2, ends, version, version2))
                self.assertTrue(path2.endswith(ends),
                                "Path [%s] is not ends with [%s]" % (path2, ends,))

            ends = "rss.gif"
            orig_path = get_version_path(path, None)
            print("Path [%s] have to ends with [%s], version [%s->]\n" % (orig_path, ends, version))
            self.assertTrue(orig_path.endswith(ends),
                            "Path [%s] is not ends with [%s]" % (path2, ends,))
            orig_path = get_version_path(path)
            print("Path [%s] have to ends with [%s], version [%s->]\n" % (orig_path, ends, version))
            self.assertTrue(orig_path.endswith(ends),
                            "Path [%s] is not ends with [%s]" % (path2, ends,))

    def test_get_version_path_do_not_check_file(self):
        for version in settings.FILEBROWSER_VERSIONS:
            path = get_version_path("3/rss.gif", version, check_file=False)
            ends = "3/rss_" + version + ".gif"
            print("Path [%s] have to ends with [%s], version [%s]\n" % (path, ends, version))
            self.assertTrue(path.endswith(ends),
                            "Path [%s] is not ends with [%s]" % (path, ends,))

            for version2 in settings.FILEBROWSER_VERSIONS:
                path2 = get_version_path(path, version2, check_file=False)
                ends = "3/rss_" + version2 + ".gif"

                print("Path [%s] have to ends with [%s], version [%s->%s]\n" % (path2, ends, version, version2))
                self.assertTrue(path2.endswith(ends),
                                "Path [%s] is not ends with [%s]" % (path2, ends,))

            ends = "3/rss.gif"
            orig_path = get_version_path(path, version_prefix='', check_file=False)
            print("Path [%s] have to ends with [%s], version [%s->]\n" % (orig_path, ends, version))
            self.assertTrue(orig_path.endswith(ends),
                            "Path [%s] is not ends with [%s]" % (path2, ends,))
            orig_path = get_version_path(path, check_file=False)
            print("Path [%s] have to ends with [%s], version [%s->]\n" % (orig_path, ends, version))
            self.assertTrue(orig_path.endswith(ends),
                            "Path [%s] is not ends with [%s]" % (path2, ends,))
