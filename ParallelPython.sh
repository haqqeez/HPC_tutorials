#!/bin/bash

########################################################################################

### Enter your 3-letter initials below; this is used to name jobs based on Animal ID
### Note that this and the email input are both OPTIONAL! If you put nothing, or put something incorrect, the script will likely still launch your jobs.
###### Except that the job names might look strange and you won't get e-mail notifications

# for example, the animal "ZHA001" has initials "ZHA" and IDlength 6
initials="ZHA"
IDlength=6

### Enter your e-mail below
email="computezee@gmail.com"

### Enter the full parent directory for analysis in the () brackets (default is pwd)
### The script will search from *this* directory onwards for BehavCam_0 folders.
root_directory=$(pwd)

# Path to your scripts
slurmscript='ISOMAP.sl'
python_directory='/lustre03/project/rrg-markpb68/m3group/Haqqee/GitHub/'
scripts_directory='/lustre03/project/rrg-markpb68/m3group/Haqqee/GitHub/'
pyscript="ISOMAP_example.py" #can have abc_*.py if wanting to loop through multiple scripts
taskname="ISOMAP" # name displayed for job

TIMLIM=0:15:00
CPUS=12
RAM=48G # avoid using MEM as a variable as it might be a reserved word

# set number of CPU to use, which is the same as CPUS
NUM_CPUS=$CPUS

########################################################################################
## Should not need to change anything below this line, unless you know what you're doing!

data=$(find $root_directory -type d -name "BehavCam_0")
#SCRIPTs=$(find $python_directory -maxdepth 1 -type f -exec basename {} \; -name $python_name)

for session in $data; do
  cd $session
  cd ../

  echo "Analyzing $session"
  ID=$initials${session#*$initials}
  animal=${ID::$IDlength}
  date=202${session#*202}; date=${date::10}
  animalID="$animal-$date$end"
  ID="$taskname-$animal-$date"

  cp "$scripts_directory$slurmscript" .

  sed -i -e "s|SCRIPTPATH|$python_directory$pyscript|g" $slurmscript
  sed -i -e "s|OUTNAME|$ID|g" $slurmscript
  sed -i -e "s|TASKNAME|$ID|g" $slurmscript
  sed -i -e "s|ANIMAL|$animal|g" $slurmscript
  sed -i -e "s|MYEMAIL|$email|g" $slurmscript

  sed -i -e "s|NUM_CPUS|$NUM_CPUS|g" $slurmscript
  # sed -i -e "s|ARG2|$ARG2|g" $slurmscript
  # sed -i -e "s|ARG3|$ARG3|g" $slurmscript
  # sed -i -e "s|ARG4|$ARG4|g" $slurmscript
  # sed -i -e "s|ARG5|$ARG5|g" $slurmscript
  # sed -i -e "s|ARG6|$ARG6|g" $slurmscript
  # sed -i -e "s|ARG7|$ARG7|g" $slurmscript

  sed -i -e "s|TIMLIM|$TIMLIM|g" $slurmscript
  sed -i -e "s|CPUS|$CPUS|g" $slurmscript
  sed -i -e "s|RAM|$RAM|g" $slurmscript
  
  sbatch $slurmscript
  sleep 0.4
done
