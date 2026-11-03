import tempfile
import unittest
from pathlib import Path
from sensor_log_audit import audit, main


class AuditTests(unittest.TestCase):
    def check_csv(self, data, period=1):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'samples.csv'
            path.write_text(data, encoding='utf-8')
            return audit(path, period)

    def test_regular_samples(self):
        self.assertEqual(self.check_csv('time_s,value\n0,2\n1,3\n2,4\n'), (3, []))

    def test_gap_order_and_bad_values(self):
        count, issues = self.check_csv('time_s,value\n0,1\n2,2\n2,3\n3,nan\n')
        self.assertEqual(count, 3)
        self.assertEqual(len(issues), 3)
        self.assertIn('sampling gap', issues[0])
        self.assertIn('not increasing', issues[1])
        self.assertIn('invalid', issues[2])

    def test_header_and_period_validation(self):
        with self.assertRaises(ValueError):
            self.check_csv('time,value\n0,1\n')
        with self.assertRaises(ValueError):
            self.check_csv('time_s,value\n0,1\n', 0)

    def test_duplicate_required_headers_are_rejected(self):
        for data in ('time_s,time_s,value\n0,1,2\n',
                     'time_s,value,value\n0,1,2\n'):
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.check_csv(data)

    def test_no_valid_samples(self):
        count, issues = self.check_csv('time_s,value\n')
        self.assertEqual(count, 0)
        self.assertEqual(issues, ['no valid samples'])

    def test_cli_missing_file(self):
        self.assertEqual(main(['/no/such/sensor-log.csv', '--period', '1']), 2)


if __name__ == '__main__':
    unittest.main()
