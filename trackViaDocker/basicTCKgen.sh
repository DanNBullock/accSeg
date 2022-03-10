NUM_FIBERS=`jq -r '.fiberNumber' config.json`
MIN_LENGTH=`jq -r '.minLength' config.json`
MAX_LENGTH=`jq -r '.maxLength' config.json`
fod=`jq -r '.wmFOD' config.json`

#fod=/home/heilb028/bullo092/Tractography_For_Dan/Chandler/Preprocessed/wmfod.mif
#pathOut=/home/heilb028/bullo092/test/test.tck
pathOut=../testdata/output/tractogram.tck


tckgen $fod -algorithm iFOD2 \
           -select $NUM_FIBERS -seed_dynamic $fod \
            -minlength $MIN_LENGTH -maxlength $MAX_LENGTH -max_attempts_per_seed 1000 \
           $pathOut
