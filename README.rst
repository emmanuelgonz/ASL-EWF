ASL-CLI
=======
ASL-CLI provides a command line interface (CLI) for the AirSurf-Lettuce application created by the `Crops Phenomics Group
<https://github.com/Crop-Phenomics-Group/>`_. This CLI allows you to quickly feed inputs through the command line, rather than using a GUI. 

Running ASL-CLI pipeline
------------------------------------
* First install the GitHub repo:

.. code-block:: RST
   
   git clone https://github.com/emmanuelgonz/ASL-EWF.git
|
* Then, go to the ASL-EWF direcoty and change permissions as follows:

.. code-block:: RST 

   cd ASL-EWF
   chmod -R 755 *   
|
* Go the to src directory and run the depend.sh which contains all the necessary dependencies to run ASL-CLI:

.. code-block:: RST

   cd src/
   ./depend.sh
|
* Now you're ready to count lettuce! All you have to do is run the following command line argument:

.. code-block:: RST

   python3 asl_cli.py run_pipeline <image_file_directory> <image_filename> <model_directory>
|
* Here is an example to run a sample image. This is an example, make sure to change to your own directory.

.. code-block:: RST
   
   python3 asl_cli.py run_pipeline '/home/emmanuel/Documents/ASL-EWF/test_images/sample_region1.png' 'sample_region1' '/home/emmanuelgonzalez/ASL-EWF/model/trained_model_new.h5'
|

.. note:: If using your own images, please make sure to add them to the 

|
After running this file, the following files will be output into a sub folder inside the data directory:

- boxes.npy

- loop_vars.npy

- probs.npy

- size_labels.npy

- sizes.png

- counts.png

- grey_conversion.png

- harvest_regions.png

- <filename>fielddata.csv


   
