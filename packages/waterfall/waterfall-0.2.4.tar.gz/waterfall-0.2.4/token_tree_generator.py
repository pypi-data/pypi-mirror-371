from typing import List
from manim import *
import numpy as np
import torch
from waterfall.WatermarkerBase import Watermarker
from waterfall.watermark import PROMPT, PRE_PARAPHRASED
from transformers.cache_utils import DynamicCache

config.pixel_width = 3840
config.pixel_height = 1600
config.frame_rate = 15

watermarker = Watermarker(model = 'meta-llama/Meta-Llama-3.1-8B-Instruct', device="auto")

# def convert_to_node(tree):
#     """Recursively convert a (key, value, children) nested list tree 
#     to a Node-based tree.
#     """
#     key, val, children = tree
#     node_children = [convert_to_node(c) for c in children]
#     return Node(key, val, node_children)

def compress_tree(node):
    """
    Recursively compress chains of single-child nodes.
    Rule: if node has exactly 1 child, concatenate keys,
    keep parent value, and recurse.
    """
    key, val, children = node

    # First compress children recursively
    compressed_children = [compress_tree(child) for child in children]

    # While there is exactly 1 child, merge into parent
    while len(compressed_children) == 1:
        child_key, child_val, child_children = compressed_children[0]
        key = key + child_key   # concat keys
        # value stays as parent's val
        compressed_children = child_children  # adopt child's children

    return (key, val, compressed_children)

class Node:
    def __init__(self, key, prob, children=None):
        self.key = key
        self.prob = prob
        self.children = children or []
    def get_key(self):
        self.expand_children()
        return self.key
    def get_prob(self):
        self.expand_children()
        return self.prob
    def get_children(self):
        self.expand_children()
        return self.children
    def expand_children(self):
        if isinstance(self.children, tuple):
            self.children = expand_(*self.children)
        new_children = []
        for child in self.children:
            if not child.key.strip():
                for i in child.get_children():
                    print(f"concatenating {child.key} and {i.key}")
                    i.key = child.key + i.key
                    i.prob = child.prob * i.prob
                new_children.extend(child.get_children())
            else:
                new_children.append(child)
        self.children = sorted(new_children, key=lambda c: c.prob)


def Droplet(radius=1.0, color=RED, opacity=0.6, stroke_width=2, top_angle=50):
    """
    Returns a droplet-shaped VMobject:
    - bottom is a 270° arc of a circle
    - top is a flat line tangent to the circle
    """
    R = radius
    
    # Arc: from 135° (top-left) to 45° (top-right), going counterclockwise
    arc = Arc(
        radius=R,
        start_angle=(top_angle/2/180)*PI,
        angle=-PI * (1 + top_angle/180),        # sweep down and around
    )

    # Get arc boundary points
    arc_points = arc.get_points()

    # Add a flat top line (close the path)
    top = np.array([0, R/np.sin((top_angle/2/180)*PI), 0])

    # Concatenate arc + line back
    all_points = np.vstack([arc_points, top, arc_points[0]])
    # all_points = arc_points

    # Build single shape
    droplet = VMobject()
    droplet.set_points_as_corners(all_points)
    droplet.set_fill(color, opacity)
    droplet.set_stroke(color, stroke_width)

    return droplet

def watermark_symbol(radius=1, color=BLUE, background_opacity=0.1) -> Mobject:
    # Circle
    circle = Droplet(radius=radius, color=color, opacity=background_opacity, stroke_width=0)

    # Small sine squiggle inside the circle
    squiggle_size = 0.6 * radius
    squiggle = ParametricFunction(
        lambda t: np.array([t, 0.5*radius*np.sin(t / squiggle_size * np.pi), 0]),  # small squiggle
        t_range=[-squiggle_size, squiggle_size],
        color=BLACK,
        stroke_width=radius * 12
    )

    # Group them
    shape = VGroup(circle, squiggle)

    # Feathered edges effect
    # (Manim doesn't have native feathering, but you can fake it
    # by overlaying multiple circles with decreasing opacity)
    blurred_edges = VGroup(*[
        Droplet(radius=radius * i, color=color, opacity=background_opacity, stroke_width=0)
        for i in np.linspace(1, 0.7, 5)
    ])

    final_shape = VGroup(blurred_edges, shape)
    return final_shape

m, c = -0.012892119897959181, -0.9999984801020411

def single_pass(input_ids, top_k = 4):
    with torch.no_grad():
        output = watermarker.model(
            input_ids = input_ids.to(watermarker.model.device),
            attention_mask = torch.ones_like(input_ids)
            )
    return [(idx, prob) for prob, idx in zip(*torch.nn.functional.softmax(output.logits[...,-1,:].squeeze().cpu(), dim=-1).topk(k=top_k, dim=0))]

def expand(input_ids, remainder_tokens : int, top_k = 4, threshold = 0.01) -> List:
    if remainder_tokens <= 0:
        return []
    res = []
    pass_results = single_pass(input_ids, top_k = top_k)
    for i, (idx, prob) in enumerate(pass_results):
        if prob <= threshold:
            continue
        new_input_ids = torch.cat([input_ids.clone(), idx.view(1,1)], dim=-1)
        if idx == watermarker.tokenizer.eos_token_id:
            res.append(Node(watermarker.tokenizer.decode(idx), prob.item(), []))
            continue
        res.append(Node(watermarker.tokenizer.decode(idx), prob.item(), (new_input_ids, remainder_tokens-1, top_k, threshold)))
    return res

def single_pass_(input_ids, past_key_values=DynamicCache(), top_k = 4):
    with torch.no_grad():
        output = watermarker.model(
            input_ids = input_ids.to(watermarker.model.device),
            attention_mask = torch.ones_like(input_ids),
            past_key_values=past_key_values,
            use_cache=past_key_values is not None
        )
        logits = output.logits[...,-1,:].cpu()
        past_key_values = output.past_key_values
    return [tuple(zip(idx, prob)) for prob, idx in zip(*torch.nn.functional.softmax(logits, dim=-1).topk(k=top_k, dim=1))], past_key_values

def repeat_dynamic_cache(cache: DynamicCache, n: int) -> DynamicCache:
    """
    Repeat a DynamicCache n times along the batch dimension.
    Returns a new DynamicCache.
    """
    new_cache = DynamicCache()
    for layer_idx in range(len(cache)):
        k, v = cache[layer_idx]  # each is (batch, num_heads, seq_len, head_dim)
        k = k.repeat(n, 1, 1, 1)
        v = v.repeat(n, 1, 1, 1)
        new_cache.update(k, v, layer_idx=layer_idx)
    return new_cache

def select_batch_from_cache(cache: DynamicCache, batch_idx: int) -> DynamicCache:
    """
    Extract the i-th batch entry from a DynamicCache and return a new DynamicCache.
    """
    new_cache = DynamicCache()
    for layer_idx in range(len(cache)):
        k, v = cache[layer_idx]
        # slice along batch dimension and keep dims
        k_i = k[batch_idx:batch_idx+1, ...]
        v_i = v[batch_idx:batch_idx+1, ...]
        new_cache.update(k_i, v_i, layer_idx=layer_idx)
    return new_cache

def expand_(input_ids, prev_results, remainder_tokens : int, top_k = 4, threshold = 0.01, bar=None, past_key_values = DynamicCache()) -> List:
    if remainder_tokens <= 0:
        if bar is not None:
            bar.update(1)
        return []
    idxs = [i[0] for i in prev_results if i[1] > threshold]
    prev_results_ = [i for i in prev_results if i[1] > threshold]
    idxs = torch.stack(idxs)
    if (idxs == watermarker.tokenizer.eos_token_id).any():
        prev_results_ = []
    if bar is not None:
        bar.total -= (len(prev_results) - len(prev_results_)) * (top_k ** (remainder_tokens - 1))
    new_input_ids = torch.cat([input_ids.repeat(idxs.shape[0],1), idxs.unsqueeze(1)], dim=-1)
    if past_key_values is not None and len(past_key_values):
        past_key_values = repeat_dynamic_cache(past_key_values, idxs.shape[0])
    pass_results, past_key_values = single_pass_(new_input_ids, past_key_values, top_k = top_k)
    res = []
    for i, ((idx, prob), result, new_input_id) in enumerate(zip(prev_results_, pass_results, new_input_ids)):
        res.append(Node(
            watermarker.tokenizer.decode(idx), 
            prob.item(), 
            (new_input_id, result, remainder_tokens-1, top_k, threshold, bar, select_batch_from_cache(past_key_values, i) if past_key_values is not None else None)
            ))
    if past_key_values is not None:
        del past_key_values
        torch.cuda.empty_cache()
    if bar is not None:
        bar.refresh()
    return res

class TokenDecode(Scene):

    def __init__(self, watermarker, tree=None, font_size=12, seed=42, top_k=5, font="sans-serif", **kwargs):
        self.watermarker = watermarker
        self.tree = tree
        self.font_size = font_size
        self.relative_size = (font_size / -m + c) / 1860
        self.seed = seed
        self.top_k = top_k
        self.font = font
        super().__init__(**kwargs)

    def drop_watermark(self, x_pos, y_pos, y_shift, color, scale=1, speedup=1):
        image = ImageMobject("dropper.png")
        
        # Change color to BLUE (applies to non-transparent areas)
        image.set_color(color)

        # Rotate 90 degrees clockwise (use -90 for clockwise)
        image.rotate(-90 * DEGREES)  # or use PI/2 radians

        image.scale(0.3 * scale)

        image.move_to(np.array([x_pos, y_pos, 0]))
        image.shift(LEFT * (image.get_left()[0] - image.get_center()[0]) * 0.9 + UP * y_shift)

        droplet = watermark_symbol(radius=0.15 * scale, color=color, background_opacity=0.4)
        droplet.next_to(np.array([x_pos, image.get_bottom()[1], 0]), DOWN, buff=0.1 * scale)

        self.play(FadeIn(image), run_time=0.15 * speedup)

        self.play(FadeIn(droplet), run_time=0.15 * speedup)

        self.wait(0.15 * speedup)

        self.play(droplet.animate.shift(DOWN * y_shift), run_time=0.5 * speedup)

        self.wait(0.15 * speedup)

        self.play(FadeOut(image), FadeOut(droplet), run_time=0.15 * speedup)

    def construct(self):
        if self.tree is None:
            raise ValueError("No tree provided")
        self.rng = np.random.default_rng(self.seed)

        root = self.tree
        selected_tokens = []
        current_sentence_mob = None

        def get_chains(node):
            rows = []
            for c in node.get_children():
                chain = ""
                key = c.get_key()
                while len(c.get_children()) == 1:
                    c = c.get_children()[0]
                    key += c.get_key()
                child = c
                finished = False
                for _ in range(3):
                    if not child.get_children():
                        finished = True
                        break
                    best = max(child.get_children(), key=lambda x: x.get_prob() or 0)
                    chain += "" + best.get_key()
                    child = best
                if not finished:
                    chain += " ..."
                rows.append((key, c.get_prob(), chain.strip(), c.get_children()))
            return rows

        current_sentence_mob = None
        vertical_spacing = self.relative_size * 0.6
        left_margin = Text("0.00", font=self.font, font_size=self.font_size).get_width()
        scene_width, scene_height = config.frame_width, config.frame_height
        rows_y_offset = -scene_height / 2 + (self.top_k + 1) * vertical_spacing
        while root.get_children():
            rows = get_chains(root)
            if not rows:
                break
                
            # Calculate current sentence position
            current_sentence = "".join(selected_tokens) if selected_tokens else ""

            # Phase 1: Show rows with probabilities and greyed chains
            row_mobs = []
            prob_mobs = []
            
            # First pass: calculate positions to align chains
            max_tok_x_end = -float('inf')
            row_data = []
            
            probs = np.array([p for (_, p, _, _) in rows])
            probs = probs / probs.sum()  # Normalize probabilities
            for i, ((tok, _, chain, _), p) in enumerate(zip(rows, probs)):
                # Position calculations
                y_pos = rows_y_offset - i * vertical_spacing

                # Create sentence prefix if exists
                if current_sentence:
                    prefix_mob = Text(current_sentence + "", font=self.font, color=WHITE, font_size=self.font_size, should_center=False)
                    prefix_mob.set_fill(opacity=0)  # Make it transparent for positioning only
                    prefix_mob.to_edge(LEFT).shift(UP * y_pos)
                    prefix_x_end = prefix_mob.get_right()[0]
                else:
                    prefix_mob = None
                    prefix_x_end = config.frame_x_radius * -1 + left_margin + 0.15

                # Create probability text (left-aligned after prefix)
                prob_mob = Text(f"{p:.2f}", font=self.font, color=WHITE, font_size=self.font_size, should_center=False)
                y_offset = (m * self.font_size + c - prob_mob.get_center()[1])
                prob_mob.next_to(np.array([prefix_x_end, y_pos, 0]), RIGHT, buff=-left_margin)
                prob_mob.shift(DOWN * y_offset)
                prob_x_end = prob_mob.get_right()[0]

                # Create token text
                tok_mob = Text(tok, font=self.font, color=WHITE, font_size=self.font_size, should_center=False)
                if len(tok_mob) > 0:
                    y_offset = (m * self.font_size + c - tok_mob.get_center()[1])
                    tok_mob.next_to(np.array([prob_x_end, y_pos, 0]), RIGHT, buff=self.relative_size * 0.2)
                    tok_mob.shift(DOWN * y_offset)
                    tok_x_end = tok_mob.get_right()[0]
                    max_tok_x_end = max(max_tok_x_end, tok_x_end)
                row_data.append((y_pos, prefix_mob, prob_mob, tok_mob, chain))
            
            # Second pass: create chains aligned to the same x position
            for i, (y_pos, prefix_mob, prob_mob, tok_mob, chain) in enumerate(row_data):
                # Create chain text (greyed out) - all chains start at the same x position
                if chain:
                    print(chain)
                    chain_mob = Text(chain, font=self.font, color=GREY, font_size=self.font_size, should_center=False)
                    y_offset = (m * self.font_size + c - chain_mob.get_center()[1])
                    chain_mob.next_to(np.array([max_tok_x_end, y_pos, 0]), RIGHT, buff=self.relative_size * 0.2)
                    # Align chain vertically with the token (bottom alignment)
                    # chain_mob.align_to(tok_mob, DOWN)
                    chain_mob.shift(DOWN * y_offset)
                else:
                    chain_mob = None

                # Update row_data to include chain_mob for later reference
                row_data[i] = (y_pos, prefix_mob, prob_mob, tok_mob, chain, chain_mob)

                # Collect all parts for this row
                row_parts = [prob_mob, tok_mob]
                # if prefix_mob:
                #     row_parts.insert(0, prefix_mob)
                # else:
                #     row_parts.insert(0, None)
                if chain_mob:
                    row_parts.append(chain_mob)
                
                row_group = VGroup(*row_parts)
                row_mobs.append(row_group)
                prob_mobs.append(prob_mob)
                
                # self.play(FadeIn(prob_mob), FadeIn(tok_mob), run_time=0.15)
                # if chain_mob:
                #     self.play(FadeIn(chain_mob), run_time=0.15)
            print(1)
            prob_mobs = [i[0] for i in row_mobs if i and len(i) >= 1]
            if prob_mobs:
                self.play(FadeIn(*prob_mobs, run_time=0.15))
            print(2)
            tok_mobs = [i[1] for i in row_mobs if i and len(i) >= 2]
            if tok_mobs:
                self.play(FadeIn(*tok_mobs, run_time=0.15))
            print(3)
            chain_mobs = [i[2] for i in row_mobs if i and len(i) >= 3]
            if chain_mobs:
                self.play(*[Write(i, run_time=0.15) for i in chain_mobs])

            self.wait(0.15)

            # Phase 2: Fade out old probabilities, fade in new blue probabilities
            new_probs = np.array([p for (_, p, _, _) in rows])
            new_probs = np.exp(np.log(new_probs) + np.sin(self.rng.random(new_probs.shape) * 2 * np.pi) * 2)
            new_probs /= new_probs.sum()  # Normalize new probabilities
            new_prob_mobs = []
            
            # Create new probability texts
            for i, new_p in enumerate(new_probs):
                new_prob_mob = Text(f"{new_p:.2f}", font=self.font, color=BLUE, font_size=self.font_size, should_center=False)
                new_prob_mob.move_to(prob_mobs[i].get_center())
                new_prob_mobs.append(new_prob_mob)

            # Animate probability change
            print(4)
            fade_out_anims = [FadeOut(prob_mob) for prob_mob in prob_mobs]
            print(5)
            fade_in_anims = [FadeIn(new_prob_mob) for new_prob_mob in new_prob_mobs]

            self.drop_watermark(prob_mobs[0].get_center()[0], rows_y_offset + self.relative_size * 1.3, vertical_spacing * 0.5, BLUE, scale=self.relative_size)
            print(6)
            self.play(*fade_out_anims, run_time=0.15)
            self.remove(*prob_mobs)
            print(7)
            self.play(*fade_in_anims, run_time=0.15)
            
            # Update row_mobs with new probability texts
            new_row_mobs = []
            for i, (y_pos, prefix_mob, old_prob_mob, tok_mob, chain, chain_mob) in enumerate(row_data):
                # Create new row with updated probability
                new_row_parts = [new_prob_mobs[i], tok_mob]
                # if prefix_mob:
                #     new_row_parts.insert(0, prefix_mob)
                if chain_mob:
                    new_row_parts.append(chain_mob)
                
                new_row_group = VGroup(*new_row_parts)
                new_row_mobs.append(new_row_group)
            
            # Replace the old row_mobs with new ones
            row_mobs = new_row_mobs
            prob_mobs = new_prob_mobs

            self.wait(0.5)

            # Phase 3: Select one row based on probabilities
            probs = np.array([p if (token.strip() and (len(children) != 1)) else 0.0 for (token, p, _, children) in rows])
            if probs.sum() == 0:
                probs = np.array([p for (_, p, _, _) in rows])
            idx = self.rng.choice(range(len(rows)), p=probs / probs.sum())
            selected_row = row_mobs[idx]
            selected_token = rows[idx][0]

            # Fade out non-selected rows
            print(8)
            fade_out_anims = []
            if len(selected_row) > 2:
                fade_out_anims.append(FadeOut(*list(selected_row)[2:]))
            selected_row = VGroup(*list(selected_row)[:2])  # Remove chain from selected row
            print(9)
            for i, row in enumerate(row_mobs):
                if i != idx:
                    fade_out_anims.append(FadeOut(row))

            print(10)
            if fade_out_anims:
                self.play(*fade_out_anims, run_time=0.15)

            # Move selected row up and fade out chain
            # target_y = 1.5
            # selected_row_copy = selected_row.copy()

            row_parts = list(selected_row)
            self.play(selected_row.animate.shift(UP * (idx * vertical_spacing)), run_time=0.8)

            self.wait(0.3)

            # Phase 4: Animate token joining the sentence
            selected_tokens.append(selected_token)
            new_sentence = "".join(selected_tokens)
            
            # Create new sentence text
            new_sentence_mob = Text(new_sentence, font=self.font, color=WHITE, font_size=self.font_size, should_center=False)
            y_offset = (m * self.font_size + c - new_sentence_mob.get_center()[1])
            new_sentence_mob.to_edge(LEFT, buff=0.15)
            new_sentence_mob.move_to(np.array([new_sentence_mob.get_center()[0], rows_y_offset + vertical_spacing, 0]))
            new_sentence_mob.shift(DOWN * y_offset)

            # Fade out the selected row and fade in the new sentence
            print(11)
            self.play(FadeOut(selected_row, run_time=0.3))

            print(12)
            self.play(FadeIn(new_sentence_mob), run_time=0.15)
            if current_sentence_mob:
                self.remove(current_sentence_mob)

            current_sentence_mob = new_sentence_mob
            self.wait(0.15)

            # Update root for next iteration
            root = Node(new_sentence, None, rows[idx][3])
            # break