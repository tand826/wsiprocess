WSIDIR="."
WSIS=(CMU-1.ndpi)
SAVE_TOS=(/ . "")
METHODS=(none Classification Detection Segmentation)
FOREGROUNDS=(0 0.5000001 1.0)
ONANNOTATIONS=(0 0.5000001 1.0)
ANNOTATIONS=(CMU-1_classification.xml CMU-1_detection.xml CMU-1_segmentation.xml)
RULES=(rule.json)
PATCH_SIZES=(0 1 256 0.1 4096)
OVERLAP_SIZES=(0 1 256 0.1 4096)
MAGNIFICATIONS=(40 20 10 1)

wsi=${WSIS[0]}
rule=${RULES[0]}
for ((i=0;i<3;i++)); do save_to=${SAVE_TOS[i]}
for ((i=0;i<4;i++)); do method=${METHODS[i]}
for ((i=0;i<3;i++)); do on_foreground=${FOREGROUNDS[i]}
for ((i=0;i<3;i++)); do on_annotation=${ONANNOTATIONS[i]}
for ((i=0;i<4;i++)); do annotation=${ANNOTATIONS[i]}
for ((i=0;i<3;i++)); do patch_size=${PATCH_SIZES[i]}
for ((i=0;i<3;i++)); do overlap_size=${OVERLAP_SIZES[i]}
for ((i=0;i<4;i++)); do magnification=${MAGNIFICATIONS[i]}
    echo ${WSIDIR}/${wsi} \
         ${method} \
         -st ${save_to} \
         -of ${on_foreground} \
         -oa ${on_annotation} \
         -pw ${patch_size} \
         -ph ${patch_size} \
         -ow ${overlap_size} \
         -oh ${overlap_size} \
         -ma ${magnification} \
         -ep
    wsiprocess ${WSIDIR}/${wsi} \
               ${method} \
               -st ${save_to} \
               -of ${on_foreground} \
               -oa ${on_annotation} \
               -pw ${patch_size} \
               -ph ${patch_size} \
               -ow ${overlap_size} \
               -oh ${overlap_size} \
               -ma ${magnification} \
               -ep
done; done; done; done; done; done; done; done