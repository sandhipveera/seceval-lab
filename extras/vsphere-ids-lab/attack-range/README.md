# Attack Range

A reusable, repeatable set of attack scenarios run against the target boxes so every product
is tested against the *same* stimulus. Scenarios are declarative (`scenarios/*.yml`); the
generator executes them and tags artifacts with the run id.

Golden rule: targets defined in `docker/targets/` are the ONLY legitimate destinations. See
`docs/SAFETY.md`.
