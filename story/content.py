LEVEL_STORIES = {
    2: {
        'title': 'Level 2 Story',
        'button_label': 'Enter Level 2',
        'next_url': '/levels/2/',
        'story_lines': [
            'After solving the strawberry waste problem, you have barely finished celebrating when the store manager calls you over with a screenshot from the inventory system.',
            'The system shows an egg inventory value of only 100. The manager is worried about a stockout. Eggs are a staple product with frequent repeat purchases, and running out could drive away core customers.',
            'Based on that single unit-free number in the system, the manager pushes an urgent recommendation: "Order 50 cartons of eggs from the supplier right now. The inventory looks almost empty, and if we wait, we will not restock in time."',
            'Your job is to verify the inventory and sales records, standardize the measurement units, judge the real egg inventory position, and then decide whether to order or not order so the store avoids both overstock and shortage.',
        ],
        'help_description': 'Review the story, then enter Level 2 and make the egg reorder decision only after checking the inventory and sales data.',
    },
    3: {
        'title': 'Level 3 Story',
        'button_label': 'Enter Level 3',
        'next_url': '/levels/3/',
        'story_lines': [
            'Last weekend, the supermarket ran a buy-one-get-one promotion in fresh produce. After the campaign ended, the store manager brought you customer reviews and sales data with obvious excitement.',
            'Weekend fresh-produce sales were up 40% compared with the usual baseline, and the campaign collected more than 20 positive customer reviews.',
            'Encouraged by the partial feedback and the visible sales growth, the manager recommends continuing the same promotion immediately: "The sales were great and customers loved it. Profit must have gone up too."',
            'Your task is to analyze the full promotion dataset, judge the real effect, and decide whether the store should continue or stop the promotion before the fresh-produce department takes a bigger loss.',
        ],
        'help_description': 'Review the story, then enter Level 3 and decide whether the fresh-produce promotion should continue.',
    },
    4: {
        'title': 'Level 4 Story',
        'button_label': 'Enter Level 4',
        'next_url': '/levels/4/',
        'story_lines': [
            "You just stabilized the fresh-produce business when finance hands the store manager this month's revenue chart and asks for support on next month's marketing budget decision.",
            'The manager sees the chart and immediately concludes that marketing worked extremely well this month. The graph looks steep, and the visual jump appears dramatic.',
            'Influenced by the misleading chart, the manager gives a confident recommendation: "Look how much this chart jumped. That must be the result of our $5,000 marketing budget. Next month we should double the spend and push revenue even higher."',
            'Your job is to verify the raw data behind the chart, judge the real revenue growth, and choose whether to double, maintain, or reduce the marketing budget without wasting cost or damaging profit.',
        ],
        'help_description': 'Review the story, then enter Level 4 and decide how the marketing budget should be adjusted.',
    },
    5: {
        'title': 'Level 5 Story',
        'button_label': 'Enter Level 5',
        'next_url': '/levels/5/',
        'story_lines': [
            'The contract with the current fresh-produce core supplier is about to expire, and the store manager hands you the data of two candidate suppliers for a joint decision.',
            'The manager looks only at the total profit figures and quickly recommends Supplier A: "Supplier A has a total margin of 15%, while Supplier B is only 12%. Choosing A should obviously make the store more money."',
            "But the detailed category data tells a different story. The store's fresh-produce business is heavily concentrated in high-margin categories, and the two suppliers perform very differently inside each subgroup.",
            "Your job is to recognize Simpson's paradox in the supplier comparison, match the data to the store's real category structure, and choose the supplier that actually maximizes fresh-produce profit.",
        ],
        'help_description': 'Review the story, then enter Level 5 and decide which supplier is actually better for the store.',
    },
    6: {
        'title': 'Level 6 Story',
        'button_label': 'Enter Level 6',
        'next_url': '/levels/6/',
        'story_lines': [
            'Your store decisions are becoming more precise, so the manager now asks you to help with operating-hours planning. Recently the store has received 10 late-night customer complaints saying that closing at 10 PM is too early.',
            'Influenced by those complaint samples, the manager recommends extending business hours from 10 PM to midnight immediately: "Clearly customers want us open later. If we extend the schedule, we can keep them and earn more night sales."',
            'But those complaints are only a small and biased late-night sample. The full customer-flow data shows that traffic drops sharply after 8 PM, and customer volume from 10 PM to midnight is extremely low.',
            'Your job is to judge whether the complaint sample is representative, compare night traffic with labor and utility cost, and decide whether the store should extend operating hours or not.',
        ],
        'help_description': 'Review the story, then enter Level 6 and decide whether the supermarket should extend operating hours.',
    },
    7: {
        'title': 'Level 7 Story',
        'button_label': 'Enter Level 7',
        'next_url': '/levels/7/',
        'story_lines': [
            'After multiple business challenges, you have become the store manager\'s most trusted problem-solver. This month the supermarket opened takeout channels on both Meituan and Ele.me, hoping to expand revenue.',
            'But the platform order data is messy and inconsistent, and finance cannot tell whether the takeout business is truly profitable or losing money. The manager is unsure whether to keep the channel running.',
            'Looking only at the rough order volume, the manager gives a hasty judgment: "There are plenty of takeout orders every day, so we must be making money. Even if it is not much, it cannot be a loss. Let us keep it open first."',
            'Your final task is to standardize the raw cross-platform order data, remove duplicates, unify the counting units, combine the data with operating cost, and decide whether the takeout channel is actually profitable or loss-making.',
        ],
        'help_description': 'Review the story, then enter Level 7 and complete the final takeout reconciliation challenge.',
    },
}
