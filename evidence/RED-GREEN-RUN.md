# Red/Green Run Instructions and Evidence

## Red run (intentional failure demonstration)

This project includes a deliberate red run example that was generated to satisfy assessment evidence requirements.

### What was intentionally broken
The test assertion was temporarily changed from expecting a 400 response to expecting a 500 response in the empty-message validation test.

### Why the test should fail
The API correctly returns 400 for an empty complaint message. Changing the assertion to 500 intentionally makes the test fail, proving the workflow is being validated and not faked.

### Actual failing output
The actual red-run output is stored in [red-run.txt](red-run.txt).

### How it was fixed
The test file was restored to the correct assertion immediately after the failed run.

## Green run (final passing verification)

The final green run is stored in [green-run.txt](green-run.txt).

### Actual final result
The latest verification passed:

```text
7 passed, 1 warning in 12.55s
```

## Commands to rerun manually

From the project root:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -q
```

To create a fresh red-run, intentionally change a failing assertion in the tests and rerun the command above. Restore the file immediately after capturing the failure output.
