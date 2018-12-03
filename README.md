# Terrestrial
Celery-backed REST API around Terraform.

**Not battle tested yet!**

## Why?

Imagine getting a request from a team, like: "we want to be able to quickly deploy a fully configured environment, end to end, with this version of this app, and that version of that app... and it should be running on top of a fresh DB snapshot from that other environment. Oh, and we want to do that as a part of CI on every PR. And also from a Slack chat. And this env should really just kill itself after a while if we forget to drop it manually."

Other portion of input data: I tend to have every piece of infrastructure implemented as a code (usually) with Terraform.

That's pretty much the background of what Terrestrial aims to solve for me and how it's shaped.

Also, automation if fun.

## How?

Terrestrial wraps Terraform, exposing a set of API endpoints, which, being triggered, perform Terraform actions as if you do them manually.

Now, since Terraform apply/destroy and even plan can take quite a while, you would want to schedule the whole run as some kind of a background job, and not wait for the API call to finish. Hence Celery.

It should also work with hosted CI systems (Travis/CircleCI, name it), and at the same time be capable of provisioning things which are often only accessible from inside the infrastructure (like, create a user and a database in DBMS, which resides in a private network), which Terraform conveniently has providers for. Hence, not having it all implemented as a set of CI jobs.

## Requirements
* Python 3.6
* Redis
* [Remote state storage](https://www.terraform.io/docs/state/remote.html) enabled for each and every(!) Terraform configuration
* Credentials for Terraform providers in use set properly

## How to run this thing
1) Place your terraform configurations in meaningfully named subdirectories under `configurations` directory, or ship them elsehow (like in a Docker volume).
These can as well be git submodules or smth, and can in turn rely on other modules as long as they're structured in a way that you can run terraform from root of a particular configuration's folder.

You'll end up with structure like this:
```
configurations
├── test
│   ├── test.tf
│   └── variables.tf
└── test1
    └── test.tf
```
2) Come up with a decent API token and ship it as env variable. Same thing applies to any providers you have in configurations - credentials must be shipped

3) Build and/or deploy Terrestrial wherever you can reach its API

### Running manually
```bash
# Logs will be a mess
$ redis-server &
$ ./worker.py &
$ API_TOKEN=dev ./api.py
```
API server will run in dev mode on port 5000

### Running in Docker with Compose
``` bash
$ docker-compose up --build
```
Will build and start the whole stack with API accessible on port 8000

## Configuration
Environment variables:
```bash
# Mandatory
API_TOKEN=<long random string> # if not set, auth will fail

# Optional
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
TF_CONF_PATH=<path to Terraform configurations directory> # defaults to "configurations" in Terrestrial root directory
```

## API
Terrestrial comes with a simple bash client, located under `cli` folder, which does most of the following in a more convenient way.

Assuming API is accessible at
```bash
TERRESTRIAL_ADDR="http://localhost:8000"
TERRESTRIAL_TOKEN=<same as API token you previously set>
```

Auth header has a form of
```bash
AUTH_HEADER="Authorization: Token $TERRESTRIAL_TOKEN"
```

List all available configurations:
```bash
$ curl -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/configurations
```

Show configuration state. Equivalent of 'terraform show':
```bash
$ curl -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/configurations/<config_name>

# Example:
$ curl -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/configurations/test

# Redirects to
$ curl -H "$AUTH_HEADER"$TERRESTRIAL_ADDR/api/v1/configurations/test/show
```

Perform Terraform action on configuration:
```bash
$ curl -X POST -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/configurations/<config_name>/<action>

# Example:
$ curl -X POST -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/configurations/test/apply

# Passing variables to Terraform:
$ curl -X POST -d "var1=foo&var2=bar" -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/configurations/test/apply

# Running job asynchronously:
$ curl -X POST -d "var1=foo&var2=bar" -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/configurations/test/apply\?async
# this will emit a task ID which can later be used in tasks portion of the API

# Delaying job execution:
$ curl -X POST -d "var1=foo&var2=bar" -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/configurations/test/destroy\?async\&delay=600
# will run the job with 10 minutes delay
```

Working in Terraform workspaces.

All configuration endpoints are similar;
workspace name goes after configuration name
```bash
$ curl -X POST -H "$AUTH_HEADER"  $TERRESTRIAL_ADDR/api/v1/configurations/<config_name>/<workspace>/<action>

# Example
$ curl -X POST -d "var1=foo&var2=bar" -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/configurations/test/test-workspace/apply
```

Listing **active** tasks:
```bash
$ curl -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/tasks
```

Getting task status:
```bash
$ curl -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/tasks/<task_id>

# Example:
$ curl -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/tasks/17f00479-4730-40b7-aa83-e507a71c5b5b
```

Getting task result:
```bash
$ curl -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/tasks/<task_id>/result

# Example:
$ curl -H "$AUTH_HEADER" $TERRESTRIAL_ADDR/api/v1/tasks/17f00479-4730-40b7-aa83-e507a71c5b5b/result
```

## Limitations
I can't stress the importance of remote state storage being enabled for every configuration. If you don't have it - you'll lose your Terraform states, and will very likely be unable to recover them.

By default, Terrestrial prevents parallel execution of the jobs working on the same configuration, in the same workspace with the same set of variables. Lock will be release when the job finishes, or in 10 minutes (by default) after it started, whichever happens first.

## Notes
- Worker won't start if any configuration fails to pass a validation (aka `terraform validate`)

## TODOs
- [ ] Test it properly
- [ ] Limit auth attempts
- [ ] Make logging consistent
- [ ] Enhance security model
- [ ] Handle Terraform configurations isolation in a smarter way
