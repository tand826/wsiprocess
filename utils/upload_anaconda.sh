VERSION=0.6

anaconda login
conda skeleton pypi wsiprocess --output-dir ./conda_tmp
for python_version in 3.6 3.7 3.8
do
    # in the root directory of wsiprocess
    conda-build --python ${python_version} . --output-folder ./conda_tmp
    conda convert --platform all ./conda_tmp/*/wsiprocess-${VERSION}-py${python_version}_0.tar.bz2 -o conda_tmp
    for platform in linux-32 linux-64 linux-aarch64 linux-armv6l linux-armv7l linux-ppc64le osx-64 win-32 win-64
    do
        anaconda upload ./conda_tmp/${platform}/wsiprocess-${VERSION}-py${python_version}_0.tar.bz2
    done
done
rm -rf ./conda_tmp
