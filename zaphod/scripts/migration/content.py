from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

try:
    from scrappy import model as scrappy_model
    from crowdsupply import model as cs_model
    from scrappy.model import meta as scrappy_meta
except ImportError:
    scrappy_meta = scrappy_model = cs_model = None

from ... import model

from . import utils


def migrate_articles(settings):
    for old_article in scrappy_meta.Session.query(scrappy_model.Article):
        print("article %s" % old_article.name)
        article = model.Article(
            id=old_article.id,
            name=old_article.name,
            teaser=old_article.teaser,
            body=old_article.body.text,
            published=old_article.published,
            listed=old_article.listed,
            show_heading=old_article.show_heading,
            show_article_list=old_article.show_article_list,
            category=old_article.category,
            created_by_id=old_article.created_by_id,
            created_time=old_article.created_time,
            updated_by_id=old_article.updated_by_id,
            updated_time=old_article.updated_time,
        )
        model.Session.add(article)
        utils.migrate_aliases(settings, old_article, article)
        utils.migrate_image_associations(settings, old_article, article)
        model.Session.flush()


def migrate_tags(settings):
    tag_map = {}
    for old_tag in scrappy_meta.Session.query(cs_model.Tag):
        print("tag %s" % old_tag.name)
        tag = model.Tag(
            id=old_tag.id,
            name=old_tag.name,
            teaser=old_tag.name,
            body=old_tag.body.text,
            published=old_tag.published,
            listed=old_tag.listed,
            created_by_id=old_tag.created_by_id,
            created_time=old_tag.created_time,
            updated_by_id=old_tag.updated_by_id,
            updated_time=old_tag.updated_time,
        )
        model.Session.add(tag)
        utils.migrate_aliases(settings, old_tag, tag)
        tag_map[old_tag] = tag
        model.Session.flush()
    return tag_map


def migrate_creators(settings):
    creator_map = {}
    for old_creator in scrappy_meta.Session.query(cs_model.Creator):
        print("creator %s" % old_creator.name)
        creator = model.Creator(
            id=old_creator.id,
            name=old_creator.name,
            teaser=old_creator.teaser,
            location=old_creator.location,
            home_url=old_creator.home_url,
            body=old_creator.body.text,
            published=old_creator.published,
            listed=old_creator.listed,
            created_by_id=old_creator.created_by_id,
            created_time=old_creator.created_time,
            updated_by_id=old_creator.updated_by_id,
            updated_time=old_creator.updated_time,
        )
        model.Session.add(creator)
        utils.migrate_aliases(settings, old_creator, creator)
        utils.migrate_image_associations(settings, old_creator, creator)
        creator_map[old_creator] = creator
        model.Session.flush()
    return creator_map


def launched_on_crowd_supply(old_project):
    whitelist_ids = [
        610,  # Essential System
        365,  # PF Solution Insole
    ]
    if old_project.id in whitelist_ids:
        return True
    q = scrappy_meta.Session.query(cs_model.PledgeLevel).\
        join(cs_model.PledgeLevel.cart_items.of_type(
            cs_model.PledgeCartItem)).\
        filter(cs_model.PledgeLevel.project_id == old_project.id)
    return bool(q.first())


def migrate_projects(settings, creator_map, tag_map):
    project_map = {}
    product_map = {}
    option_value_map = {}
    batch_map = {}
    for old_project in scrappy_meta.Session.query(cs_model.Project):
        print("  project %s" % old_project.name)
        project = model.Project(
            id=old_project.id,
            creator=creator_map[old_project.creator],
            name=old_project.name,

            prelaunch_vimeo_id=old_project.preview_vimeo_id,
            prelaunch_teaser=old_project.teaser,
            prelaunch_body=u'',

            crowdfunding_vimeo_id=old_project.vimeo_id,
            crowdfunding_teaser=old_project.teaser,
            crowdfunding_body=old_project.body.text,

            available_vimeo_id=old_project.vimeo_id,
            available_teaser=old_project.teaser,
            available_body=old_project.body.text,

            published=old_project.published,
            listed=old_project.listed,
            gravity=old_project.gravity,
            target=old_project.target,
            start_time=old_project.start_time,
            end_time=old_project.end_time,
            suspended_time=old_project.suspended_time,
            created_by_id=old_project.created_by_id,
            created_time=old_project.created_time,
            updated_by_id=old_project.updated_by_id,
            updated_time=old_project.updated_time,

            accepts_preorders=(old_project.stage in (2, 3)),
            include_in_launch_stats=launched_on_crowd_supply(old_project),
            pledged_elsewhere_amount=old_project.pledged_elsewhere_amount,
            pledged_elsewhere_count=old_project.pledged_elsewhere_count,

            direct_transactions=old_project.direct_transactions,
            crowdfunding_fee_percent=old_project.fee_percent,
            successful=old_project.pledged_amount > old_project.target,
        )
        model.Session.add(project)
        utils.migrate_aliases(settings, old_project, project)
        utils.migrate_image_associations(settings, old_project, project)
        project_map[old_project] = project
        for old_tag in old_project.tags:
            print("    assoc tag %s" % old_tag.name)
            project.tags.add(tag_map[old_tag])
        for old_update in old_project.updates:
            print("    update %s" % old_update.name)
            update = model.ProjectUpdate(
                id=old_update.id,
                project=project,
                name=old_update.name,
                teaser=old_update.teaser,
                body=old_update.body.text,
                published=old_update.published,
                listed=old_update.listed,
                created_by_id=old_update.created_by_id,
                created_time=old_update.created_time,
                updated_by_id=old_update.updated_by_id,
                updated_time=old_update.updated_time,
            )
            model.Session.add(update)
            utils.migrate_aliases(settings, old_update, update)
            utils.migrate_image_associations(settings, old_update, update)
        for old_pledge_level in old_project.levels:
            print("    pledge level %s" % old_pledge_level.name)
            intl_available = old_pledge_level.international_available
            intl_surcharge = old_pledge_level.international_surcharge
            product = model.Product(
                id=old_pledge_level.id,
                project=project,
                name=old_pledge_level.name,
                international_available=intl_available,
                international_surcharge=intl_surcharge,
                non_physical=old_pledge_level.non_physical,
                gravity=old_pledge_level.gravity,
                published=old_pledge_level.published,
                price=old_pledge_level.price,
                accepts_preorders=(old_project.stage in (2, 3)),
            )
            model.Session.add(product)
            utils.migrate_image_associations(settings, old_pledge_level,
                                             product)
            product_map[old_pledge_level] = product
            for old_option in old_pledge_level.all_options:
                print("      option %s" % old_option.name)
                option = model.Option(
                    name=old_option.name,
                    gravity=old_option.gravity,
                    published=old_option.enabled,
                )
                product.options.append(option)
                for old_value in old_option.all_values:
                    print("        value %s" % old_value.description)
                    value = model.OptionValue(
                        description=old_value.description,
                        gravity=old_value.gravity,
                        published=old_value.enabled,
                    )
                    option.values.append(value)
                    option_value_map[old_value] = value
            for old_batch in old_pledge_level.batches:
                print("      batch %s" % old_batch.id)
                batch = model.Batch(
                    qty=old_batch.qty,
                    delivery_date=old_batch.delivery_date
                )
                batch_map[old_batch] = batch
                product.batches.append(batch)
        for old_owner in old_project.ownerships:
            print("    ownership %s" % old_owner.account.email)
            new_owner = model.ProjectOwner(
                project=project,
                user_id=old_owner.account_id,
                title=old_owner.title,
                can_change_content=old_owner.can_change_content,
                can_post_updates=old_owner.can_post_updates,
                can_receive_questions=old_owner.can_receive_questions,
                can_manage_payments=old_owner.can_manage_stripe,
                can_manage_owners=old_owner.can_manage_owners,
                show_on_campaign=old_owner.show_on_campaign,
            )
            model.Session.add(new_owner)
        model.Session.flush()

    for old_project, new_project in project_map.items():
        new_project.related_projects[:] = [project_map[old_rel] for old_rel in
                                           old_project.related_projects]

    return project_map, product_map, option_value_map, batch_map


def migrate_provider_types(settings):
    provider_type_map = {}
    for old_provider_type in \
            scrappy_meta.Session.query(cs_model.ProviderType):
        print("  provider type %s" % old_provider_type.name)
        provider_type = model.ProviderType(
            id=old_provider_type.id,
            name=old_provider_type.name,
            teaser=old_provider_type.teaser,
            body=old_provider_type.body.text,
            published=old_provider_type.published,
            listed=old_provider_type.listed,
            created_by_id=old_provider_type.created_by_id,
            created_time=old_provider_type.created_time,
            updated_by_id=old_provider_type.updated_by_id,
            updated_time=old_provider_type.updated_time,
        )
        model.Session.add(provider_type)
        utils.migrate_aliases(settings, old_provider_type, provider_type)
        utils.migrate_image_associations(settings, old_provider_type,
                                         provider_type)
        provider_type_map[old_provider_type] = provider_type
        model.Session.flush()
    return provider_type_map


def migrate_providers(settings):
    provider_type_map = migrate_provider_types(settings)
    for old_provider in scrappy_meta.Session.query(cs_model.Provider):
        print("  provider %s" % old_provider.name)
        provider = model.Provider(
            id=old_provider.id,
            name=old_provider.name,
            teaser=old_provider.teaser,
            body=old_provider.body.text,
            published=old_provider.published,
            listed=old_provider.listed,
            mailing=utils.convert_address(old_provider.mailing),
            home_url=old_provider.home_url,
            created_by_id=old_provider.created_by_id,
            created_time=old_provider.created_time,
            updated_by_id=old_provider.updated_by_id,
            updated_time=old_provider.updated_time,
        )
        model.Session.add(provider)
        for old_type in old_provider.types:
            provider.types.add(provider_type_map[old_type])
        utils.migrate_aliases(settings, old_provider, provider)
        utils.migrate_image_associations(settings, old_provider, provider)
        model.Session.flush()
