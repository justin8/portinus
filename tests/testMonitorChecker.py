import unittest
from unittest.mock import patch

import portinus
from portinus.monitor import checker


class testMonitorChecker(unittest.TestCase):

    def setUp(self):
        self.container_string = \
            "containerid1\n" \
            "containerid2\n" \
            "containerid3\n" \
            "containerid4\n" \
            "containerid5\n" \
            "containerid6\n" \
            "containerid7\n"
        self.container_list = [
            "containerid1",
            "containerid2",
            "containerid3",
            "containerid4",
            "containerid5",
            "containerid6",
            "containerid7",
        ]

    def test_check_container_health_healthy(self):
        container = lambda: None
        container.attrs = {"State": {"Health":{"Status": "healthy"}}}
        self.assertTrue(checker.check_container_health(container))

    def test_check_container_health_pending(self):
        container = lambda: None
        container.attrs = {"State": {"Health":{"Status": "pending"}}}
        self.assertTrue(checker.check_container_health(container))

    def test_check_container_health_unhealthy(self):
        container = lambda: None
        container.attrs = {"State": {"Health":{"Status": "unhealthy"}}}
        self.assertFalse(checker.check_container_health(container))

    @patch.object(portinus, 'ComposeSource')
    @patch('subprocess.check_output')
    def test_get_comopse_container_ids(self, fake_check_output, fake_compose_source):
        fake_check_output().decode.return_value = self.container_string
        expected_result = self.container_list

        result = checker.get_compose_container_ids('foo')
        self.assertEqual(result, expected_result)

    @patch('docker.from_env')
    def test_get_monitored_containers(self, fake_docker):
        fake_docker().containers.list.return_value = [
            lambda: None,
            lambda: None,
            lambda: None,]
        fake_docker().containers.list.return_value[0].attrs = {"State":{"Health"}}
        fake_docker().containers.list.return_value[1].attrs = {"State":{"Health"}}
        fake_docker().containers.list.return_value[2].attrs = {"State":{}}

        monitored_containers = checker.get_monitored_containers()
        self.assertEqual(len(monitored_containers),2)

    @patch.object(checker, 'get_compose_container_ids')
    @patch.object(checker, 'get_monitored_containers')
    def test_monitored_compose_containers(self, fake_get_monitored_containers,
                                          fake_get_compose_container_ids):
        fake_get_compose_container_ids.return_value = self.container_list
        fake_get_monitored_containers.return_value = [
                lambda: None,
                lambda: None,
                lambda: None,
                lambda: None,]

         # Exists in self.container_list
        fake_get_monitored_containers.return_value[0].id = self.container_list[0]
        fake_get_monitored_containers.return_value[1].id = self.container_list[1]
        fake_get_monitored_containers.return_value[2].id = self.container_list[3]
        # Does not exist
        fake_get_monitored_containers.return_value[3].id = "unmonitoredcontainerid20"

        monitored_compose_containers = checker.get_monitored_compose_containers('foo')
        self.assertEqual(len(monitored_compose_containers),3)

    @patch.object(checker, 'check_container_health')
    @patch.object(checker, 'get_monitored_compose_containers')
    @patch.object(portinus, 'Service')
    def test_run_healthy(self, fake_service,
                         fake_get_monitored_compose_containers,
                         fake_check_container_health):
        fake_check_container_health.return_value = True
        fake_get_monitored_compose_containers.return_value = [
                lambda: None,
                lambda: None,]
        fake_get_monitored_compose_containers.return_value[0].attrs = {"Name": "foo"}
        fake_get_monitored_compose_containers.return_value[0].id = self.container_list[0]
        fake_get_monitored_compose_containers.return_value[1].attrs = {"Name": "bar"}
        fake_get_monitored_compose_containers.return_value[1].id = self.container_list[0]

        ret = checker.run('foo')
        self.assertTrue(ret)
        self.assertFalse(fake_service().restart.called)

    @patch.object(checker, 'check_container_health')
    @patch.object(checker, 'get_monitored_compose_containers')
    @patch.object(portinus, 'Service')
    def test_run_unhealthy(self, fake_service,
                         fake_get_monitored_compose_containers,
                         fake_check_container_health):
        fake_check_container_health.return_value = False
        fake_get_monitored_compose_containers.return_value = [
                lambda: None,
                lambda: None,]
        fake_get_monitored_compose_containers.return_value[0].attrs = {"Name": "foo"}
        fake_get_monitored_compose_containers.return_value[0].id = self.container_list[0]
        fake_get_monitored_compose_containers.return_value[1].attrs = {"Name": "bar"}
        fake_get_monitored_compose_containers.return_value[1].id = self.container_list[0]

        ret = checker.run('foo')
        self.assertFalse(ret)
        self.assertTrue(fake_service().restart.called)
