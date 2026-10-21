from django.test import SimpleTestCase
from .network_engine import simulate_network

class NetworkEngineTests(SimpleTestCase):
    def test_two_stage_conservation_and_determinism(self):
        p={"arrival_min":6,"horizon":240,"seed":42,"stages":[
            {"name":"Recepción","service_min":4,"servers":2},
            {"name":"Atención","service_min":7,"servers":3}]}
        a=simulate_network(p);b=simulate_network(p)
        self.assertEqual(a,b)
        self.assertEqual(a["arrivals"],a["completed"]+a["in_system_at_close"])
        self.assertEqual(len(a["stages"]),2)
        self.assertTrue(all(0<=s["utilization"]<=1 for s in a["stages"]))

    def test_stage_bounds(self):
        with self.assertRaises(ValueError):simulate_network({"stages":[{"name":"Solo","service_min":5,"servers":1}]})
        with self.assertRaises(ValueError):simulate_network({"stages":[{"name":str(i),"service_min":5,"servers":1} for i in range(11)]})
