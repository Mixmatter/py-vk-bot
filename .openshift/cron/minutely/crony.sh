#!/bin/bash

cd ${OPENSHIFT_REPO_DIR}"crons/"
for pfile in $(ls *.py)
do
	echo $pfile
	python ${OPENSHIFT_REPO_DIR}"crons/"$pfile
done