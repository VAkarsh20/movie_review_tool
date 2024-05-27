from utils.proofread_utils import *

def proofread(proto):
    counter = 0
    request_batch = 1
    model = create_model()

    # Direction
    if proto.review.direction.comments != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.direction.comments = proofread_comments(proto.review.direction.comments, model)
        counter += 1

    # Story
    if proto.review.story.comments != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.story.comments = proofread_comments(proto.review.story.comments, model)
        counter += 1

    # Screenplay
    if proto.review.screenplay.comments != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.screenplay.comments = proofread_comments(proto.review.screenplay.comments, model)
        counter += 1
 
    # Acting
    if proto.review.acting.rating != "":
        for idx, actor in enumerate(proto.review.acting.performance):
            if actor.comments != "":
                if wait(counter, request_batch):
                    request_batch += 1
                actor.comments = proofread_comments(actor.comments, model)
                proto.review.acting.performance[idx].CopyFrom(actor)
                counter += 1
        if proto.review.acting.cast.comments != "":
            if wait(counter, request_batch):
                request_batch += 1
            proto.review.acting.cast.comments = proofread_comments(proto.review.acting.cast.comments, model)
            counter += 1

    # Score
    if proto.review.score.comments != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.score.comments = proofread_comments(proto.review.score.comments, model)
        counter += 1
    
    # Soundtrack
    if proto.review.soundtrack.comments != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.soundtrack.comments = proofread_comments(proto.review.soundtrack.comments, model)
        counter += 1

    # Cinematography
    if proto.review.cinematography.comments != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.cinematography.comments = proofread_comments(proto.review.cinematography.comments, model)
        counter += 1

    # Editing
    if proto.review.editing.comments != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.editing.comments = proofread_comments(proto.review.editing.comments, model)
        counter += 1

    
    # Sound
    if proto.review.sound.comments != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.sound.comments = proofread_comments(proto.review.sound.comments, model)
        counter += 1

    # Visual Effects
    if proto.review.visual_effects.comments != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.visual_effects.comments = proofread_comments(proto.review.visual_effects.comments, model)
        counter += 1

    # Animation
    if proto.review.animation.comments != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.animation.comments = proofread_comments(proto.review.animation.comments, model)
        counter += 1

    # Production Design
    if proto.review.production_design.comments != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.production_design.comments = proofread_comments(proto.review.production_design.comments, model)
        counter += 1

    # Makeup
    if proto.review.makeup.comments != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.makeup.comments = proofread_comments(proto.review.makeup.comments, model)
        counter += 1

    # Costumes
    if proto.review.costumes.comments != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.costumes.comments = proofread_comments(proto.review.costumes.comments, model)
        counter += 1

    # Plot Structure
    if proto.review.plot_structure != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.plot_structure = proofread_comments(proto.review.plot_structure, model)
        counter += 1
    
    # Pacing
    if proto.review.pacing != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.pacing = proofread_comments(proto.review.pacing, model)
        counter += 1

    # Climax
    if proto.review.climax != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.climax = proofread_comments(proto.review.climax, model)
        counter += 1

    # Tone
    if proto.review.tone != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.tone = proofread_comments(proto.review.tone, model)
        counter += 1

    # Final Notes
    if proto.review.final_notes != "":
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.final_notes = proofread_comments(proto.review.final_notes, model)
        counter += 1

    # Overall
    if proto.review.overall not in ["","Overall, "]:
        if wait(counter, request_batch):
            request_batch += 1
        proto.review.overall = proofread_comments(proto.review.overall, model)
        counter += 1

    return proto