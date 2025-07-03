import replicate

input = {
    "prompt": "A breaking news ident, followed by a TV news presenter excitedly telling us: We interrupt this programme to bring you some breaking news... Veo 3 is now live on Replicate. Then she shouts: Let's go!\n\nThe TV presenter is an epic and cool punk with pink and green hair and a t-shirt that says \"Veo 3 on Replicate\""
}

output = replicate.run(
    "google/veo-3",
    input=input
)
with open("output.mp4", "wb") as file:
    file.write(output.read())
#=> output.mp4 written to disk