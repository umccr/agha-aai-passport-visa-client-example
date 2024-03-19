# GA4GH AAI (Passport/Visa) Clients

This repository contains an example "client" in a GA4GH passport ecosystem.

The "client" is a (fake) research environment website - a web portal that
allows "research" to be done using other GA4GH data protocols such as `htsget`
and `drs`.

This research environment is a simple (and again - entirely fake!) React
front-end. The aim is that is can be hosted in multiple back-end languages (to give
example of passport/visas in multiple languages).

* Python

The entire client (front-end/back-end) is designed to be run *solely*
locally on a developers machine. It is *not* production-level code
that is suitable for deployment out of the box into Internet
exposed environment (for instance, it embeds known
"secrets" in the source code).

This code *is*
designed to run against the publicly deployed passport/visa test bed
infrastructure - so other than
the locally running "client" no other services need to be spun up
on the developers machine.


## Build

A standard Unix `make` binary will be useful for all the setup/running
tasks - but is not actually a requirement for any particular code.
Make is only useful here because of the polyglot languages/environments
across the whole project.

The rest of
these instructions will assume that `make` is being used. If `make` is
not available, read the `Makefile` to see what commands are being
executed for any individual language.

### Requirements

For the front-end, the client needs a working NodeJS installation.

For each back-end, obviously it will need the programming tools of
the given language (i.e. Python for Python, NodeJS for Typescript).

### Setup

For the front-end, we need to install the NodeJS modules.

```shell
make setup-front-end
```

For the back-end, we need to establish a Python virtual environment.

```shell
make setup-python-back-end
```

If you believe you have a reasonable developers machine with all
the tools in place, you can just ask for the whole thing to be
setup.

```shell
make setup
```

### Build

```shell
make build
```




