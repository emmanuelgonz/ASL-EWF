ASL-CLI
=======
ASL-CLI provides a command line interface (CLI) for the AirSurf-Lettuce application created by the `Crops Phenomics Group
<https://github.com/Crop-Phenomics-Group/>`_. This CLI allows you to quickly feed inputs through the command line, rather than using a GUI. 

Running AirSurf-Lettuce CLI pipeline
------------------------------------
To use the CLI, download the repo and run the whole_pipe function found in the aslfire2.py file as follows:

* First install all dependencies by running:

.. code::
   
   git clone https://github.com/emmanuelgonz/ASL-EWF.git
   cd ASL-EWF
   chmod -R 755 * 
   cd src/
   ./depend.sh

* Now you're ready to count lettuce! All you have to do is run the following command line argument:

.. code::

   python3 aslwindow.py run_pipeline <image_file_directory> <image_filename> <model_directory>

* Here is an example to run a sample image. This is an example, make sure to change to your own directory.

.. code::
   
   python3 aslwindow.py run_pipeline '/home/emmanuel/Documents/ASL-EWF/test_images/sample_region1.png' 'sample_region1' '/home/emmanuelgonzalez/ASL-EWF/model/trained_model_new.h5'

.. note::   
   If using your own images, please make sure to add them to the 

After running this file, the following files will be output into ..data/<filename>/:
- boxes.npy

- loop_vars.npy

- probs.npy

- size_labels.npy

- sizes.png

- counts.png

- grey_conversion.png

- harvest_regions.png

- <filename>fielddata.csv


   
