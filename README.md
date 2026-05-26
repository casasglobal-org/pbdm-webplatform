# Description

This repository includes code for the CASAS-PBDM Web Platform, initially developed for the case study on olive/olive oil under the [MED-GOLD project](<https://doi.org/10.3030/776467>), as part of the [MED-GOLD ICT ecosystem for climate services in agriculture](<https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/horizon-results-platform/32534;keyword=med-gold>), and further developed under the [TEBAKA project](<https://www.dtascarl.org/en/projects-and-initiatives/use-case-technology-transfer/tebaka/>).

[MED-GOLD CASAS-PBDM workflow infographic](https://doi.org/10.5281/zenodo.7928703):

![CASAS-PBDM infographic](med-gold_casas-pbdm_infographic.png?raw=true)

[PBDM workflow at ESA-SUREDOS24](https://doi.org/10.5281/zenodo.11374208):

![PBDM workflow at ESA-SUREDOS24](PBDM-workflow-ESA-SUREDOS24.png?raw=true)

See also [TEBAKA GeoStory](https://tebaka.planetek.it/catalogue/#/geostory/37) and [TEBAKA Web API demo](https://d14jvp6nch1neo.cloudfront.net/)

The MED-GOLD project has received funding from the European Union's Horizon 2020 Research and Innovation programme under Grant agreement No. 776467. Project TEBAKA (project ID: ARS01_00815) was co-funded by the European Union - ERDF and ESF, “PON Ricerca e Innovazione 2014-2020”.

This last version was funded by #TODO LUIGI

includes implementation of automated download and update of global AgERA5 weather data from the [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/) to run the CASAS-PBDM Web API workflow.

A short introduction and description follows that provides context for the CASAS-PBDM related code:

CASAS Global (Center for the Analysis of Sustainable Agricultural Systems, see <http://www.casasglobal.org/>) physiologically based demographic models (CASAS-PBDMs) are one of the key existing technology components of the MED-GOLD project (Turning climate-related information into added value for traditional MEDiterranean Grape, OLive and Durum wheat food systems, see <https://doi.org/10.3030/776467>). Note that CASAS Global CEO Andrew Paul Gutierrez was part of the project's External Advisory Committee. The coffee system has been already developed using the PBDM approach and provides some basic info about the crop in Colombia, such as main climate-related problems including key pests. This info would serve as a starting point for developing a climate service for coffee (see Task 6.2). The model can be extended to different coffee species/cultivars and to explore its possibilities in a given set of climate conditions.

The source code for PBDMs is Borland Pascal code that is embedded in a much larger code base including PBDMs for 40 different species of plants, herbivores, parasitoids, predators, and pathogens that were published as PBDM analyses implemented in a GIS context (1), and are simply a subset of all species modeled using PBDMs. Like the rest of the PBDM code base developed over the last three decades, the Pascal code for olive and coffee is currently not licensed nor it is deposited in a code repository, and is managed by the nonprofit scientific consortium CASAS Global (<http://www.casasglobal.org/>). The PBDM algorithms as well as key innovative code such as the Pascal subroutine for distributed maturation times with and without attrition, have been published in detail (2).

The code included in this repository has been used in a research context under the MED-GOLD (3) and TEBAKA (4) projects.

1. A. P. Gutierrez, L. Ponti, in Invasive Species and Global Climate Change, L. H. Ziska, J. S. Dukes, Eds. (CABI Publishing, Wallingford, UK, 2014), pp. 271–288. [PDF](https://www.casasglobal.org/casas/wp-content/uploads/2017/04/Gutierrez-Ponti-2022b-InvasiveSpeciesGCC_proof.pdf)

2. A. P. Gutierrez, Applied population ecology: a supply-demand approach (John Wiley and Sons, New York, USA, 1996; <https://www.wiley.com/en-us/Applied+Population+Ecology%3A+A+Supply+Demand+Approach-p-9780471135869>).

3. Ponti, L., Gutierrez, A. P., Giannakopoulos, C., Varotsos, K. V., López Nevado, J., López Feria, S., Rivas González, F. W., Caboni, F., Stocchino, F., Rosati, A., Marchionni, D., Cure, J. R., Rodríguez, D., Terrado, M., De Felice, M., Dell’Aquila, A., Calmanti, S., Arjona, R., & Sanderson, M. (2024). Prospective regional analysis of olive and olive fly in Andalusia under climate change using physiologically based demographic modeling powered by cloud computing. Climate Services, 34, 100455. <https://doi.org/10.1016/j.cliser.2024.100455> (Open Access)

4. Ponti, L., Gutierrez, A. P., Metz, M., Haas, J., Panzenböck, E., Neteler, M., Baldacchino, F., Ambrico, A., Baviello, G., Calvitti, M., Dell’Aquila, A., Calmanti, S., Lampazzi, E., Miceli, V., Cuna, D., Stocchino, F., & Carroccio, D. (2024, May 29). Realistic daily dynamics of olive and olive fly at 250 m resolution using cloud-gap-filled canopy temperature data from MODIS LST calibrated with MODIS NDVI. Super-Resolution and Downscaling for EO and Earth Science (SUREDOS24), 29-31 May 2024, ESA-ESRIN, Frascati, Italy, <https://suredos24.esa.int/>, Frascati, Italy. <https://doi.org/10.5281/zenodo.11374208> (Open Access)

For further information, please contact Luigi Ponti (<luigi.ponti@enea.it>)

## pbdm-workflow

Workflow to run PBDM executables compiled from Pascal source code.

## Source Code Structure and Usage

The repository is organized into several key directories, each serving a specific purpose within the CASAS-PBDM web platform.

### `casas_web_portal/`

This is the main Django web application that provides the user interface and API for interacting with the PBDM models.

* **`webapp/`**: Contains the core logic for the web portal. `views.py` handles user requests, processes forms for submitting new jobs, and renders the HTML templates for the map interface, job details, and other pages.
* **`webapi/`**: Implements the REST API for programmatic access to the PBDM workflow.
* **`casas_web_portal/`**: Contains the main Django project settings (`settings_template.py`), URL configurations, and WSGI entry point.
* **`casas-gis/`**: This directory holds the geospatial processing scripts that are the engine of the platform.
  * **`casas_gis/`**: Contains the modern Python scripts for interacting with GRASS GIS (`grass.py`). These scripts handle tasks like importing ASCII data, projecting it, setting the computational region, performing interpolation, and generating output maps.
  * **`casas_gis_old/`**: Contains legacy shell and Perl scripts originally developed for GRASS GIS 6 and updated for GRASS GIS 8. These are useful for understanding the original workflow. The `casas-gis/README_usage_GRASS_GIS8.md` file provides detailed instructions on how to run these legacy scripts.

### `weather_grid/`

This directory contains utility scripts for pre-processing climate and weather data into a format suitable for the PBDM models and GIS workflow.

* **`netcdf_grid_extract.py`**: A crucial Python script for extracting land grid coordinates from standard climate data formats like NetCDF (used for AgERA5, CMIP6, etc.). It identifies land cells and exports their coordinates, which are then used as input for the models.
* **`grass_gis_notes.sh`**: A shell script with notes and example GRASS GIS commands for importing and processing the grid data generated by `netcdf_grid_extract.py`.

### High-Level Workflow

The general process for running a simulation via the web platform is as follows:

1. **Data Preparation (Offline)**:

   * Climate data (e.g., AgERA5) is processed using `weather_grid/netcdf_grid_extract.py` to create a list of valid land grid points for a given region.
   * PBDM models are run for these grid points, generating output text files.

2. **User Interaction (Web Portal)**:

   * A user navigates to the web portal and fills out a form to define a new "Job". This involves specifying a geographical area of interest (polygon), a date range, and the weather data source.
   * The `webapp/views.py` `add_new` view handles this request.

3. **Backend Processing**:

   * The backend identifies which pre-computed weather data grid cells intersect with the user-defined polygon.
   * For each intersecting grid cell, the system decompresses the relevant PBDM output file.
   * It then executes an external script (e.g., from `casas-gis/`) to perform geospatial analysis and generate map outputs.
   * The results are stored and can be viewed on the map interface of the web portal.

## Running with Podman Compose (Containerization)

Using `podman-compose` (or `docker-compose`) is the recommended way to run the web platform. It orchestrates the multi-container setup, which includes the web application, a PostGIS database, a Redis cache, and a Traefik reverse proxy.

### Prerequisites

* Podman and `podman-compose` installed on your system.
* A `casas.env` file in the `docker/` directory to store environment variables.

### Environment Configuration (`docker/casas.env`)

Before running the services, create a `casas.env` file inside the `docker/` directory. This file holds the configuration for the database and other services.

**Example `docker/casas.env`:**

```env
# PostgreSQL Database Settings
POSTGRES_DB=casas_db
POSTGRES_USER=casas_user
POSTGRES_PASSWORD=a_strong_and_secret_password

# Django Settings
SECRET_KEY='your-django-secret-key-here'
DEBUG=1 # Set to 0 in production
ALLOWED_HOSTS=localhost,127.0.0.1,casasweb.containers.localhost

# Traefik Production Settings (for traefik_production.yml)
EMAIL_HOST=your-email@example.com
APP_URL=your-domain.com
```

### Local Development with Traefik (`docker/traefik_local.yml`)

This setup is ideal for local development. It uses Traefik to route traffic to the Django application, which is accessible at `http://casasweb.containers.localhost`.

1. **Build and Start Services:**
   From the `docker/` directory, run:

   ```bash
   podman-compose -f traefik_local.yml up --build -d
   ```

   * `--build`: Builds the `casas_web` image from the `Dockerfile`.
   * `-d`: Runs the containers in the background.

2. **Run Database Migrations:**
   Execute the initial database migrations:

   ```bash
   podman-compose -f traefik_local.yml exec casas_web python manage.py migrate
   ```

3. **Access the Application:**

   * **Web Portal**: `http://casasweb.containers.localhost`
   * **Traefik Dashboard**: `http://localhost:8080` (to monitor services)

4. **Stopping the Services:**

   ```bash
   podman-compose -f traefik_local.yml down
   ```

### Production with Traefik and Let's Encrypt (`docker/traefik_production.yml`)

This setup is designed for a production server. It configures Traefik to automatically handle HTTPS redirection and obtain SSL certificates from Let's Encrypt.

**Prerequisites for Production:**

* Your server must be accessible from the internet with a public IP address.
* A domain name (`your-domain.com`) must be pointing to your server's IP.
* Ports 80 and 443 must be open on your server's firewall.
* Update the `APP_URL` and `EMAIL_HOST` in `docker/casas.env`.
* Set `DEBUG=0` in `docker/casas.env` and add your domain to `ALLOWED_HOSTS`.

1. **Build and Start Services:**
    From the `docker/` directory, run:

    ```bash
    podman-compose -f traefik_production.yml up --build -d
    ```

2. **Run Database Migrations & Collect Static Files:**

   ```bash
   podman-compose -f traefik_production.yml exec casas_web python manage.py migrate
   podman-compose -f traefik_production.yml exec casas_web python manage.py collectstatic --no-input
   ```

3. **Access the Application:**
  The web portal will be securely accessible at `https://your-domain.com`. Traefik will automatically redirect HTTP traffic to HTTPS.

### Alternative Setup with `nginx-proxy` (`docker/compose.yml`)

The `docker/compose.yml` file provides an alternative setup using `nginx-proxy` and its Let's Encrypt companion. This is suitable for environments where `nginx-proxy` is already used to manage other services.

**Prerequisites for `nginx-proxy`:**

1. An external Docker/Podman network named `nginx-proxy-net` must exist.
2. `nginx-proxy` and `letsencrypt-nginx-proxy-companion` containers must be running and connected to this network.

**Usage:**

1. **Start the Services:**
   From the `docker/` directory, run:

   ```bash
   podman-compose -f compose.yml up --build -d
   ```


  `nginx-proxy` will automatically detect the `casas_django` container and configure routing and SSL based on the `VIRTUAL_HOST` and `LETSENCRYPT_HOST` environment variables.
