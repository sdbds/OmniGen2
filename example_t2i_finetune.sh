# !/bin/bash
SHELL_FOLDER=$(
    cd "$(dirname "$0")"
    pwd
)
cd $SHELL_FOLDER

model_path="OmniGen2/OmniGen2"
python inference.py \
    --model_path $model_path \
    --scheduler "dpmsolver++" \
    --num_inference_step 30 \
    --height 768 \
    --width 1344 \
    --text_guidance_scale 4.0 \
    --instruction "<kamisato ayaka>, with long silky black hair and clear purple eyes. She is sitting gracefully on a plush, modern sofa with pastel pink and light blue upholstery. With her left hand, she holds a traditional Japanese folding fan (sensu) decorated with a goldfish pattern, coyly covering the lower half of her face, revealing only her smiling, mysterious eyes.
Behind her stands a magnificent Japanese six-panel folding screen, adorned with classic motifs of pine trees and cranes on a golden leaf background. The scene is illuminated by soft, gentle lighting, creating a serene and classic atmosphere." \
    --output_image_path outputs/output_t2i_finetuned.png \
    --num_images_per_prompt 1 \
    --enable_taylorseer \
    --transformer_path experiments/ft/checkpoint-40000/transformer
