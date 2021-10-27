#/bin/bash

touch /tmp/remote_pdf_path_list.txt

for path in "gs://arxiv-dataset/arxiv/arxiv/pdf" "gs://arxiv-dataset/arxiv/cs/pdf"
do
    for d in `gsutil ls $path`
        do
            `gsutil ls $d >> /tmp/remote_pdf_path_list.txt`
        done
done
