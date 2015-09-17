#!/bin/bash

cd ${OPENSHIFT_REPO_DIR}
for pfile in $(ls crons/*.py)
do
	echo $pfile
	python ${OPENSHIFT_REPO_DIR}$pfile
done