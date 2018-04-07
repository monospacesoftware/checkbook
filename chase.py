import checkbook

in_trans = checkbook.load_chase('chase.csv', '2_Amazon Credit Card')
rules = checkbook.load_rules()

skipped, uncat, out = checkbook.process_trans(in_trans, rules)

checkbook.print_trans(skipped, 'skipped')
checkbook.print_trans(uncat, 'uncategorized')

checkbook.write_ccb(out, 'ccb_chase.csv')
