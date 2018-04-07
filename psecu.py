import checkbook

in_trans = checkbook.load_psecu('psecu.csv', '1_PSECU Joint Checking')
rules = checkbook.load_rules()

skipped, uncat, out = checkbook.process_trans(in_trans, rules)

checkbook.print_trans(skipped, 'skipped')
checkbook.print_trans(uncat, 'uncategorized')

checkbook.write_ccb(out, 'ccb_psecu.csv')
