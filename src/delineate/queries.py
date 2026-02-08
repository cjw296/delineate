VIEWER = """
query {
    viewer {
        id
        name
        email
    }
}
"""

TEAMS = """
query($first: Int!, $after: String, $filter: TeamFilter) {
    teams(first: $first, after: $after, filter: $filter) {
        nodes {
            id
            name
            key
            description
            color
            icon
            private
            timezone
            createdAt
            updatedAt
            archivedAt
        }
        pageInfo { hasNextPage endCursor }
    }
}
"""

USERS = """
query($first: Int!, $after: String, $filter: UserFilter) {
    users(first: $first, after: $after, filter: $filter) {
        nodes {
            id
            name
            email
            displayName
            avatarUrl
            active
            admin
            guest
            createdAt
            updatedAt
            archivedAt
        }
        pageInfo { hasNextPage endCursor }
    }
}
"""

ISSUES = """
query($first: Int!, $after: String, $filter: IssueFilter) {
    issues(first: $first, after: $after, filter: $filter) {
        nodes {
            id
            identifier
            title
            description
            priority
            priorityLabel
            estimate
            sortOrder
            boardOrder
            url
            branchName
            dueDate
            trashed
            createdAt
            updatedAt
            completedAt
            canceledAt
            archivedAt
            state { id name type color }
            assignee { id name email }
            creator { id name email }
            team { id name key }
            project { id name }
            cycle { id name number }
            parent { id identifier }
            labels { nodes { id name color } }
        }
        pageInfo { hasNextPage endCursor }
    }
}
"""

COMMENTS = """
query($first: Int!, $after: String, $filter: CommentFilter) {
    comments(first: $first, after: $after, filter: $filter) {
        nodes {
            id
            body
            url
            createdAt
            updatedAt
            archivedAt
            issue { id identifier }
            user { id name email }
            parent { id }
        }
        pageInfo { hasNextPage endCursor }
    }
}
"""

PROJECTS = """
query($first: Int!, $after: String, $filter: ProjectFilter) {
    projects(first: $first, after: $after, filter: $filter) {
        nodes {
            id
            name
            description
            state
            progress
            health
            url
            startDate
            targetDate
            createdAt
            updatedAt
            completedAt
            canceledAt
            archivedAt
            lead { id name email }
            teams { nodes { id name key } }
        }
        pageInfo { hasNextPage endCursor }
    }
}
"""

INITIATIVES = """
query($first: Int!, $after: String, $filter: InitiativeFilter) {
    initiatives(first: $first, after: $after, filter: $filter) {
        nodes {
            id
            name
            description
            status
            color
            icon
            sortOrder
            createdAt
            updatedAt
            archivedAt
            owner { id name email }
        }
        pageInfo { hasNextPage endCursor }
    }
}
"""

CYCLES = """
query($first: Int!, $after: String, $filter: CycleFilter) {
    cycles(first: $first, after: $after, filter: $filter) {
        nodes {
            id
            name
            number
            description
            startsAt
            endsAt
            progress
            createdAt
            updatedAt
            archivedAt
            team { id name key }
        }
        pageInfo { hasNextPage endCursor }
    }
}
"""

ISSUE_LABELS = """
query($first: Int!, $after: String, $filter: IssueLabelFilter) {
    issueLabels(first: $first, after: $after, filter: $filter) {
        nodes {
            id
            name
            description
            color
            createdAt
            updatedAt
            archivedAt
            team { id name }
            parent { id name }
        }
        pageInfo { hasNextPage endCursor }
    }
}
"""

DOCUMENTS = """
query($first: Int!, $after: String, $filter: DocumentFilter) {
    documents(first: $first, after: $after, filter: $filter) {
        nodes {
            id
            title
            content
            icon
            color
            url
            createdAt
            updatedAt
            archivedAt
            project { id name }
            creator { id name email }
        }
        pageInfo { hasNextPage endCursor }
    }
}
"""

WORKFLOW_STATES = """
query($first: Int!, $after: String, $filter: WorkflowStateFilter) {
    workflowStates(first: $first, after: $after, filter: $filter) {
        nodes {
            id
            name
            type
            color
            position
            description
            createdAt
            updatedAt
            archivedAt
            team { id name key }
        }
        pageInfo { hasNextPage endCursor }
    }
}
"""

ATTACHMENTS = """
query($first: Int!, $after: String, $filter: AttachmentFilter) {
    attachments(first: $first, after: $after, filter: $filter) {
        nodes {
            id
            title
            subtitle
            url
            metadata
            groupBySource
            source
            sourceType
            createdAt
            updatedAt
            archivedAt
            issue { id identifier }
            creator { id name email }
        }
        pageInfo { hasNextPage endCursor }
    }
}
"""

PROJECT_MILESTONES = """
query($first: Int!, $after: String, $filter: ProjectMilestoneFilter) {
    projectMilestones(first: $first, after: $after, filter: $filter) {
        nodes {
            id
            name
            description
            targetDate
            sortOrder
            createdAt
            updatedAt
            archivedAt
            project { id name }
        }
        pageInfo { hasNextPage endCursor }
    }
}
"""
