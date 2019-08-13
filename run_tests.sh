module load scitools/default_legacy-current

echo "Testing CalcHums"
python test_CalcHums.py
echo "Testing basic QC routines"
python test_qc.py
echo "Testing spherical geometry routines"
python test_spherical_geometry.py
echo "Testing track check routines"
python test_track_check.py
echo "Testing Extended_IMMA"
python test_Extended_IMMA.py
echo "Testing Climatology"
python test_Climatology.py
echo "Testing YMCounter"
python test_YMCounter.py
echo "Testing Tracking QC"
python test_trackqc.py
echo "Testing BackgroundField"
python test_BackgroundField.py
