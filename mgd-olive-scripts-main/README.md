# This repository contains code generated under the the MED-GOLD case study on olive/olive oil

The following folders:

```
/casas_pbdm_coffee/
/casas_pbdm_coffee/
```

include code developed for analyzing the olive and coffee systems using physiologically based demographic models (PBDMs) in a geographic information system (GIS) context. A short introduction and description follows:

CASAS Global (Center for the Analysis of Sustainable Agricultural Systems, see http://www.casasglobal.org/) physiologically based demographic models (CASAS-PBDMs) are one of the key existing technology components of the MED-GOLD project (Turning climate-related information into added value for traditional MEDiterranean Grape, OLive and Durum wheat food systems, see https://cordis.europa.eu/project/id/776467). Note that CASAS Global CEO Andrew Paul Gutierrez is part of the project's External Advisory Committee. The capacity for modeling a variety of tri-trophic agroecosystems in a general way using PBDM agro-ecosystem models including the olive/olive fly system and the coffee system will be implemented under MED-GOLD as a scalable modern computing platform in the form of an application as a service, as part of the MED-GOLD ICT platform. The information and related added-value resulting from PBDMs will mostly accrue in terms of improved management strategy. Development of the climate service tool will entail exploration of how currently used approaches to modeling olive yield and olive fruit fly infestation based on machine learning as implemented by EC2CE can be complemented by the weather-driven PBDM approach. The coffee system has been already developed using the PBDM approach and provides some basic info about the crop in Colombia, such as main climate-related problems including key pests. This info would serve as a starting point for developing a climate service for coffee (see Task 6.2). The model can be extended to different coffee species/cultivars and to explore its possibilities in a given set of climate conditions.

This repository includes code developed under the MED-GOLD project that has received funding from the European Union's Horizon 2020 Research and Innovation programme under Grant agreement No. 776467.

The source code for PBDMs is Borland Pascal code that is embedded in a much larger code base including PBDMs for 40 different species of plants, herbivores, parasitoids, predators, and pathogens that were published as PBDM analyses implemented in a GIS context (1), and are simply a subset of all species modeled using PBDMs. Like the rest of the PBDM code base developed over the last three decades, the Pascal code for olive and coffee is currently not licensed nor it is deposited in a code repository, and is managed by the nonprofit scientific consortium CASAS Global (ttp://www.casasglobal.org/). The PBDM algorithms as well as key innovative code such as the Pascal subroutine for distributed maturation times with and without attrition, have been published in detail (2).

1. A. P. Gutierrez, L. Ponti, in Invasive Species and Global Climate Change, L. H. Ziska, J. S. Dukes, Eds. (CABI Publishing, Wallingford, UK, 2014), pp. 271–288.

2. A. P. Gutierrez, Applied population ecology: a supply-demand approach (John Wiley and Sons, New York, USA, 1996; https://www.wiley.com/en-us/Applied+Population+Ecology%3A+A+Supply+Demand+Approach-p-9780471135869).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

(to be agreed project-wise)

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

