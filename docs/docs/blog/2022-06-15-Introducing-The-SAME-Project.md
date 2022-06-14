# Welcome to the SAME Project

## The Issue with Jupyter Notebooks (Which We Love!)

Data developers and data scientists are using Jupyter notebooks to build all manner of sophisticated data and machine learning pipelines. However, when it comes to deploying these notebooks into production or higher scale environments, most platforms do not "speak Jupyter natively".

To accelerate data development, we need to collaborate to bridge this gap. We would like to propose that the larger Data Developer ecosystem needs:

* A unified, distributed-friendly method for converting the millions of notebooks already created to "backend-friendly", deployable artifacts.
* Stateless, GitOps-aware tooling that can connect to platforms seamlessly, and flexible enough to take advantage of each backend's unique features.
* A simple metadata format that enables reproducibility and portability, in local, in production and across organizational boundaries with as few changes to the developer experience as possible.

Most of all, we need all this without giving up the tool that millions of developers know and love - Jupyter.

## Introducing the SAME Project

The SAME project takes on the challenge of moving notebooks to production directly. We will give developers simple tools, via CLI, SDKs and IDE extensions, to enable building production-ready Jupyter notebooks with no/small changes to their existing workflows. The standard notebook developer won't have to learn the subtleties (or APIs) of a hosting platform - they use SAME tools & SDKs and "it will just work".

The vision of the SAME Project is to include:

* A compiler that translates user code into workflow engine specs.
* An adapter framework that can interact with workflow engines.
* A portable, extensible CLI to execute actions.
* In-notebook tools and SDKs that help users author deployable code. (Optional)

In launching our project, we have already made a great deal of progress towards this goal:

<iframe width="560" height="315"
src="/images/demo.mp4"
frameborder="0"
allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
allowfullscreen></iframe>

With just what we've built so far, we believe we have the following benefits:

* **Use the SAME tools to develop faster locally.**
* **Use the SAME tools to deploy to a distributed platform.**
* **Use the SAME tools across the application lifecycle and to collaborate.**

Our north star is a world in which developers will be able to build workflows more quickly and reliably with tools they are already familiar with. At the end of the day, developers will be able to:

* Write richer, reliable, and debuggable workflows.
* Move solutions to distributed deployments faster, solving business needs.
* Migrate solutions across environments, enabling both global-scale systems and collaboration.

## The SAME Community

SAME is entirely open-source and non-commercial. We plan on donating it to a foundation as soon as we can identify one that matches our project's goals.

What can you do? Please join our community!

### Public web content

* [Website](https://sameproject.ml)
* [Google Group](https://groups.google.com/u/2/g/same-project)
* [Slack](https://join.slack.com/t/sameproject/shared_invite/zt-lq9rk2g6-Jyfv3AXu_qnX9LqWCmV7HA)
  
### Come join our repo

* [GitHub Organization](https://github.com/SAME-Project) / [GitHub Project](https://github.com/SAME-Project/same-project)
* Try it out (build instructions included)
* Complain about missing features
* EXPERTS ONLY: Add your own

Regardless, we are very open to taking your feedback. Thank you so much - onward!

-- The Co-founders of the SAME Project ([David Aronchick](https://twitter.com/aronchick) & [Luke Marsden](https://twitter.com/lmarsden))
