import replicate

def generate(model, args):
    output = replicate.run(
        model,
        input=args
    )
    return output