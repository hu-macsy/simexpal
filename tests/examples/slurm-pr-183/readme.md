# Test setup for PR #183
Issue: `simex e list` lists experiments as 'broken' even though they are running fine in slurm.
We currently do not have integration tests in simex - but: we can use the experiment setup in this folder manually to test for this bug and similar problems if the need arises.
Usage: just run `runtest.sh` and confirm that the output has correct status (i.e. not 'broken')