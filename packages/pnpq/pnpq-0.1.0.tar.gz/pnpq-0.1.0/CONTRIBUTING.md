# Contributing

Thank you for your interest in contributing to our project. To make it as easy as possible to engage with our work, please read this short guide.

## Preparing your environment

Please see [`development-environment.md`](https://github.com/moonshot-nagayama-pj/public-documents/blob/main/engineering/development-environment.md) for more information.

## Development

We run unit tests on all pull requests using simulated hardware. Use `pytest` to run these unit tests.

For ad-hoc testing of real hardware, use `pytest hardware_tests`.

Before making a pull request, please be sure to run the script `bin/check.bash`. This will run our static analysis checks and unit tests, all of which must pass before a pull request will be accepted.

Ensure that pull requests have meaningful titles. The title will be used in the changelog.

## Discussing and proposing changes

To make a trivial change, or a change that has already been agreed to in discussions outside of GitHub, please create a pull request.

If a change might need more discussion, please create a GitHub issue in this project before working on a pull request.

## Licensing and attribution

By contributing your work to this repository, you agree to license it in perpetuity under the terms described in [`LICENSE.md`](LICENSE.md). You are also asserting that the work is your own, and that you have the right to license it to us.

If you wish to integrate our work into your own projects, please follow the attribution guidelines in `LICENSE.md`.

## Code of conduct

In order to provide a safe and welcoming environment for all people to contribute to our project, we have adopted a code of conduct, which you can read in [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Versioning and backward compatibility

We use Semantic Versioning 2.0.0 for all of our projects.

## Making a release

Follow the steps below in order to create and publish a release for PnPQ

1. Decide to create a release.
1. Run `./bin/release.bash` script and wait for it to finish.
1. Wait for the release check script in GitHub Actions to finish.
1. Edit and publish the draft in [Releases](https://github.com/moonshot-nagayama-pj/PnPQ/releases) (the generate release note function is sufficient for most cases).
1. Approve the publish action.
1. Create a PR to merge this branch (the script should open a new PR automatically).
1. Wait for approval to merge the PR, and finish!

The release script is based on steps from [Pallets release procedure](https://palletsprojects.com/contributing/release).
