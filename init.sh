echo 'user_profile_id,algorithm' >user_algorithm_mapping.csv
if [ -f log_file.txt ]
then
    rm log_file.txt
fi
touch log_file.txt
