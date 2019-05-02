from click.testing import CliRunner

from kecpkg.cli import kecpkg
from kecpkg.utils import create_file
from tests.utils import BaseTestCase, temp_chdir

TEST_SECRET_KEY = """
-----BEGIN PGP PRIVATE KEY BLOCK-----

lQIGBFzLAUQBBADZqa2AjOwDRb6D/lkuNKRFwTHF1x2SnhinTv5bosUZDRakZ6zd
dEeZiMBe6sSS9x+GTK8izkcZV6cEH8Xpcr7ngaH3bsfiiZvnI6ooyGTt/KFXP6jg
bPHEXi9zceZWIdZtZ3td4I7P52rwkPRSwEDHJcyyZYkG5/73s6Rf9xLkfQARAQAB
/gcDAoPb6jcCOLHi/RU1ynJZBz9PS+nrMUdzzRhRTKzgbhu+ijWhLUyWeXJeLtR2
1OVlPUBPVUya7nII7Puk5a0YM4m7M4GDUdrOM9pGZ6t5ocfgQ/tb+fI5FkYP6d9/
8eJaUn/OmnVl4QF2ZBBjMyWi9bJoUAa1Jq868f8qLN7YSUnJVEEx+CkMRAeP9oj/
/O7KBYn+bIRitOEqTyQyxMbBj/YLRG6F3/2kZjPDJWR/rlbpGttYIxAA+TiQnBCN
0PuLg8vTLFEcmIgsrkT8Q3ODjunJq70GII72Hf3qSM6Po1lBqlyj0RxUydFJkkQa
WQZYOKZyUbnIcOMozxFuNWoNYl8KVBoWawEvS0pzTojzwQy8PEsiqOFYH59dy0VD
2fqnM9Lf6TzcFeHwMu2Ps/vDQEKUZkOPOydAFJZw0IwozZtdPfDcccMItAXjCxjr
x/1+keOSU8V1d3wuppYAO7qve2OTYf5CZAEEJmy1ovYNWqhjcNvZ+O20LnRlc3Rr
ZXkgKEtFQ1BLRyBUT09MUyB0ZXN0aW5nIG9ubHkga2V5IDNNQVkxOSmI1AQTAQoA
PhYhBI0JL8wGC8wel87EiYehd6qyNx5oBQJcywFEAhsDBQkAAVGABQsJCAcCBhUK
CQgLAgQWAgMBAh4BAheAAAoJEIehd6qyNx5o8ZsEAInYfs7EhwUknBDbFHuZt+AE
TI80SIj/VD528EZyrDzyz5p/eeg2HQd470HDSPgwnChUJdMOKSUR7oSTxoOyGJcP
p0M/ydnmSraCOhWI8srW8edtWp16OOK5y/t7CbJ97CVOenImkSwT5uzxHgZWM9Tu
qTdggGeiZjdzXYSbq0pW
=Xq/K
-----END PGP PRIVATE KEY BLOCK-----
"""
TEST_SECRET_KEY_PASSPHRASE = "test"
TEST_SECRET_KEY_FINGERPRINT = "8D092FCC060BCC1E97CEC48987A177AAB2371E68"

class TestCommandSign(BaseTestCase):

    def test_sign_list_keys(self):
        result = self.runner.invoke(kecpkg, ['sign', '--list'])
        self.assertIn(result.exit_code, [0,1], "Results of the run were: \n---\n{}\n---".format(result.output))

    def test_add_key(self):
        with temp_chdir() as d:

            create_file('TESTKEY.asc', TEST_SECRET_KEY)
            result = self.runner.invoke(kecpkg, ['sign', '--add-key', 'TESTKEY.asc'])
            self.assertEqual(result.exit_code, 0,  "Results of the run were: \n---\n{}\n---".format(result.output))

    def test_delete_key(self):
        with temp_chdir() as d:
            create_file('TESTKEY.asc', TEST_SECRET_KEY)
            result = self.runner.invoke(kecpkg, ['sign', '--add-key', 'TESTKEY.asc'])


            result = self.runner.invoke(kecpkg, ['sign', '--delete-key', TEST_SECRET_KEY_FINGERPRINT])
            self.assertEqual(result.exit_code, 0, "Results of the run were: \n---\n{}\n---".format(result.output))

